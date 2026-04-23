#!/usr/bin/env python3
"""
EdgeIQ Labs — SSL & Domain Expiry Watcher
Professional-grade SSL certificate monitoring and domain expiry tracking.
Real features security teams actually need.
"""

import argparse
import csv
import json
import os
import signal
import socket
import ssl
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
try:
    from edgeiq_licensing import is_pro, is_bundle, require_license
except ImportError:
    def is_pro():     return True
    def is_bundle():  return True
    def require_license(tier, feat=""): return True

# ─────────────────────────────────────────────
# ANSI helpers
# ─────────────────────────────────────────────
_GRN = '\033[92m'; _YLW = '\033[93m'; _RED = '\033[91m'; _CYA = '\033[96m'
_BLD = '\033[1m'; _RST = '\033[0m'; _MAG = '\033[35m'

def ok(t):    return f"{_GRN}{t}{_RST}"
def warn(t):  return f"{_YLW}{t}{_RST}"
def fail(t):  return f"{_RED}{t}{_RST}"
def info(t):  return f"{_CYA}{t}{_RST}"
def bold(t):  return f"{_BLD}{t}{_RST}"

# ─────────────────────────────────────────────
# Security headers to check (CSP, HSTS, etc.)
# ─────────────────────────────────────────────
SECURITY_HEADERS = {
    'Content-Security-Policy':   'CSP — prevents XSS/injection',
    'Strict-Transport-Security': 'HSTS — forces HTTPS',
    'X-Frame-Options':           'Clickjacking protection',
    'X-Content-Type-Options':    'MIME sniffing protection',
    'X-XSS-Protection':          'XSS filter (legacy)',
    'Referrer-Policy':           'Referrer control',
    'Permissions-Policy':        'Feature permissions',
    'Cross-Origin-Opener-Policy':'Cross-origin isolation',
    'Cross-Origin-Embedder-Policy':'COEP — embedding rules',
}

CIPHER_SECURITY = {
    'TLS_AES_256_GCM_SHA384':  ('A', 'TLS 1.3 — Excellent'),
    'TLS_AES_128_GCM_SHA256':  ('A', 'TLS 1.3 — Excellent'),
    'TLS_CHACHA20_POLY1305_SHA256': ('A', 'TLS 1.3 — Excellent'),
    'ECDHE-RSA-AES256-GCM-SHA384': ('A', 'Forward-secret — Excellent'),
    'ECDHE-RSA-AES128-GCM-SHA256': ('A', 'Forward-secret — Good'),
    'ECDHE-RSA-CHACHA20-POLY1305': ('A', 'Forward-secret — Good'),
    'AES256-SHA':  ('B', 'TLS 1.2 — Acceptable'),
    'AES128-SHA':  ('B', 'TLS 1.2 — Acceptable'),
    '3DES-EDE-CBC': ('F', 'Vulnerable — DEPRECATED'),
    'DES-CBC3-SHA': ('F', 'Vulnerable — DEPRECATED'),
}

PROTOCOL_SECURITY = {
    'TLSv1.3': ('A', 'Current standard'),
    'TLSv1.2': ('B', 'Acceptable — configure TLS 1.3 minimum'),
    'TLSv1.1': ('F', 'Deprecated — upgrade required'),
    'TLSv1.0': ('F', 'Vulnerable — upgrade required'),
    'SSLv3':   ('F', 'Vulnerable — disable immediately'),
    'SSLv2':   ('F', 'Vulnerable — disable immediately'),
}

# ─────────────────────────────────────────────
# CVE lookup for common services (local DB)
# ─────────────────────────────────────────────
CVE_DB = {
    'nginx': {
        ('0','7'): ('HIGH', 'CVE-2019-9511', 'HTTP/2 memory denial of service'),
        ('1','9'): ('MEDIUM','CVE-2021-23017','ngx_http_parser integer overflow'),
        ('1','18'): ('HIGH','CVE-2022-41741','buffer overflow in ngx_http_mp4_module'),
    },
    'apache': {
        ('2','4'): ('HIGH','CVE-2021-41773','Path traversal in apache2 (mod_cgi)'),
        ('2','17'): ('MEDIUM','CVE-2017-15710','Session fixation in mod_session'),
    },
    'openssh': {
        ('7','1'): ('HIGH','CVE-2016-6515','DOS via crypto keyboard int'),
        ('8','0'): ('MEDIUM','CVE-2020-15778','scp mount race injection'),
        ('9','0'): ('MEDIUM','CVE-2023-38408','Remote code execution via ssh-agent'),
    },
    'httpd': {
        ('2','4'): ('HIGH','CVE-2021-41773','Apache path traversal'),
    },
    'tomcat': {
        ('9','0'): ('HIGH','CVE-2020-11996','WebSocket DOS'),
        ('8','5'): ('MEDIUM','CVE-2020-13935','Java EE MSDOS'),
    },
    'iis': {
        ('10','0'): ('MEDIUM','CVE-2021-31166','HTTP protocol denial of service'),
        ('8','5'): ('MEDIUM','CVE-2017-0143','Remote code execution (EternalBlue-related)'),
    },
    'redis': {
        ('6','0'): ('CRITICAL','CVE-2021-32625','Lua sandbox escape'),
        ('5','0'): ('HIGH','CVE-2019-10192','Arbitrary command execution'),
    },
    'postgresql': {
        ('13','0'): ('MEDIUM','CVE-2021-3206','Integer overflow in array slicing'),
        ('14','0'): ('HIGH','CVE-2022-1552','AUTOVACUUM privilege escalation'),
    },
    'mysql': {
        ('8','0'): ('MEDIUM','CVE-2021-22931','Load data local infile bypass'),
        ('5','7'): ('HIGH','CVE-2019-2433','Integer overflow in JSON'),
    },
    'mongodb': {
        ('4','0'): ('HIGH','CVE-2019-2383','JavaScript injection in eval'),
        ('5','0'): ('MEDIUM','CVE-2021-22933','Unauthenticated access risk'),
    },
}

# ─────────────────────────────────────────────
# Version parsing helpers
# ─────────────────────────────────────────────
def parse_version(banner):
    """Extract version number from service banner string."""
    if not banner:
        return None
    import re
    m = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', str(banner))
    if m:
        return (m.group(1), m.group(2), m.group(3) or '0')
    return None

def match_cve(service, version_parts):
    """Look up CVE for a detected service/version."""
    key = service.lower()
    if key not in CVE_DB:
        return []
    major, minor = version_parts[0], version_parts[1]
    for (vmaj, vmin), (sev, cve_id, desc) in CVE_DB[key].items():
        if vmaj == major and int(vmin) <= int(minor):
            return [(sev, cve_id, desc)]
    return []

# ─────────────────────────────────────────────
# SSL Info Fetcher
# ─────────────────────────────────────────────
def fetch_ssl_full(hostname, port=443, timeout=10, check_http=True):
    """Full SSL cert + security analysis."""
    result = {
        'hostname': hostname, 'port': port,
        'ok': False, 'errors': [],
        'cert': {}, 'chain': [], 'protocols': [],
        'cipher': {}, 'security_headers': {},
        'http_check': {}, 'cves': [], 'grade': 'N/A',
        'scan_time': datetime.now(timezone.utc).isoformat(),
    }

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED
        # Try to load system certs on older Pythons
        try:
            ctx.load_default_certs()
        except Exception:
            pass

        sock = socket.create_connection((hostname, port), timeout=timeout)
        ssock = ctx.wrap_socket(sock, server_hostname=hostname)

        cert_data = ssock.getpeercert()
        cipher = ssock.cipher()
        proto = ssock.version()
        sock.close()

        # Parse cert
        subject = dict(x[0] for x in cert_data.get('subject', []))
        issuer  = dict(x[0] for x in cert_data.get('issuer', []))
        not_before = datetime.strptime(cert_data['notBefore'], '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
        not_after  = datetime.strptime(cert_data['notAfter'],  '%b %d %H:%M:%S %Y %Z').replace(tzinfo=timezone.utc)
        san_list   = [v for k,v in cert_data.get('subjectAltName', []) if k == 'DNS']

        days_left = (not_after - datetime.now(timezone.utc)).days

        result['ok'] = True
        result['cert'] = {
            'subject':   subject.get('commonName', hostname),
            'issuer':    issuer.get('organizationName', issuer.get('commonName', 'Unknown')),
            'san':       san_list,
            'not_before': not_before.isoformat(),
            'not_after':  not_after.isoformat(),
            'days_left':  days_left,
            'serial':     cert_data.get('serialNumber', 'N/A'),
        }
        result['protocols'] = [proto]
        result['cipher'] = {
            'name': cipher[0] if cipher else 'N/A',
            'bits': cipher[2] if cipher else 0,
            'version': cipher[1] if cipher else 'N/A',
        }

        # Grade calculation
        grade = 'A'
        if days_left <= 7:   grade = 'F'
        elif days_left <= 30: grade = 'D'
        elif days_left <= 60: grade = 'C'
        proto_sec = PROTOCOL_SECURITY.get(proto, ('F', 'Unknown'))
        if proto_sec[0] in ('F',): grade = 'F'
        result['grade'] = grade

    except ssl.SSLCertVerificationError as e:
        result['errors'].append(('CERT_ERROR', str(e)))
    except socket.timeout:
        result['errors'].append(('TIMEOUT', 'Connection timed out'))
    except ConnectionRefusedError:
        result['errors'].append(('REFUSED', 'Port refused'))
    except Exception as e:
        result['errors'].append((type(e).__name__, str(e)))

    # HTTP security headers (only if cert check succeeded)
    if result['ok'] and check_http:
        try:
            import urllib.request
            req = urllib.request.Request(f'https://{hostname}:{port}', headers={'User-Agent': 'EdgeIQ-SSL-Watcher/1.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                for hdr, desc in SECURITY_HEADERS.items():
                    val = resp.headers.get(hdr)
                    result['security_headers'][hdr] = val or '(not set)'
        except Exception as e:
            result['http_check'] = {'ok': False, 'error': str(e)}

    return result

# ─────────────────────────────────────────────
# Banner grab service detection
# ─────────────────────────────────────────────
def grab_banner(hostname, port, timeout=5):
    """Grab service banner to identify what's running."""
    try:
        sock = socket.create_connection((hostname, port), timeout=timeout)
        # Send HTTP probe for web ports
        if port in (80, 443, 8080, 8443):
            sock.send(b'HEAD / HTTP/1.0\r\nHost: %s\r\n\r\n' % hostname.encode())
        else:
            sock.send(b'\r\n')
        sock.settimeout(timeout)
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        return banner[:200]
    except:
        return None

# ─────────────────────────────────────────────
# Port scanner (common security ports)
# ─────────────────────────────────────────────
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
    53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
    443: 'HTTPS', 465: 'SMTPS', 587: 'SMTP-SUBMIT',
    993: 'IMAPS', 995: 'POP3S', 3306: 'MySQL',
    5432: 'PostgreSQL', 6379: 'Redis', 27017: 'MongoDB',
    8080: 'HTTP-ALT', 8443: 'HTTPS-ALT', 9200: 'Elasticsearch',
}

def quick_port_check(hostname, ports=None, timeout=2):
    """Check which common ports are open."""
    if ports is None:
        ports = list(COMMON_PORTS.keys())
    open_ports = []
    for port in ports:
        try:
            sock = socket.create_connection((hostname, port), timeout=timeout)
            sock.close()
            open_ports.append(port)
        except:
            pass
    return open_ports

# ─────────────────────────────────────────────
# WHOIS domain expiry
# ─────────────────────────────────────────────
def fetch_domain_expiry(domain, warn_days=30):
    """Get domain expiry — tries python-whois then shell whois."""
    result = {
        'domain': domain, 'ok': False,
        'expiry': None, 'days_left': None,
        'registrar': None, 'nameservers': [],
        'error': None, 'warn': False,
    }

    # Try python-whois
    try:
        import whois
        w = whois.query(domain)
        if w and w.expiration_date:
            exp = w.expiration_date
            if isinstance(exp, list): exp = exp[0]
            if isinstance(exp, str):
                for fmt in ('%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d %b %Y','%Y%m%d'):
                    try:
                        exp = datetime.strptime(exp.split('.')[0], fmt).replace(tzinfo=timezone.utc)
                        break
                    except: pass
            elif not hasattr(exp, 'tzinfo'):
                exp = exp.replace(tzinfo=timezone.utc)
            days = (exp - datetime.now(timezone.utc)).days
            result['ok'] = True
            result['expiry'] = exp.isoformat()
            result['days_left'] = days
            result['registrar'] = getattr(w, 'registrar', None)
            result['nameservers'] = getattr(w, 'name_servers', []) or []
            result['warn'] = days <= warn_days
    except ImportError:
        result['error'] = 'whois library not installed — run: pip install python-whois'
    except Exception as e:
        result['error'] = str(e)

    return result

# ─────────────────────────────────────────────
# Formatters
# ─────────────────────────────────────────────
def fmt_grade(g):
    m = {'A': (ok('A'),'Excellent'), 'B': (ok('B'),'Good'), 'C': (warn('C'),'Fair'),
         'D': (warn('D'),'Poor'), 'F': (fail('F'),'Critical')}
    c, d = m.get(g, (fail('?'),'Unknown'))
    return f"{c} — {d}"

def format_ssl_verbose(r):
    lines = []
    h = r['hostname']
    if not r['ok']:
        for etype, emsg in r['errors']:
            icon = fail('✘') if 'CERT' in etype else warn('!')
            lines.append(f"  {icon} {bold(h)} — {emsg}")
        return lines

    cert = r['cert']
    days = cert['days_left']
    exp_icon = ok('✔') if days > 30 else warn('⚠') if days > 7 else fail('✘')

    lines.append(f"  {exp_icon} {bold(h)}")
    lines.append(f"     Grade:       {fmt_grade(r['grade'])}")
    lines.append(f"     Issuer:      {cert['issuer']}")
    lines.append(f"     Subject:     {cert['subject']}")
    lines.append(f"     Valid:       {cert['not_before'][:10]} → {cert['not_after'][:10]}")
    lines.append(f"     Days Left:   {days}")
    lines.append(f"     Protocol:    {r['protocols'][0]}")

    cipher_name = r['cipher']['name']
    c_sec = CIPHER_SECURITY.get(cipher_name, ('B', 'Unknown'))
    c_icon = ok('✔') if c_sec[0] in ('A','B') else warn('⚠') if c_sec[0] == 'C' else fail('✘')
    lines.append(f"     Cipher:      {c_icon} {cipher_name} ({c_sec[1]})")

    if r.get('security_headers'):
        lines.append(f"     Security Headers:")
        missing = []
        for hdr, val in r['security_headers'].items():
            if val == '(not set)':
                missing.append(hdr)
            else:
                lines.append(f"       {ok('✔')} {hdr}: {val[:60]}")
        for hdr in missing:
            lines.append(f"       {fail('✘')} {hdr}: (not set)")

    if cert.get('san'):
        lines.append(f"     SANs:       {', '.join(cert['san'][:6])}")

    return lines

def format_domain_verbose(r):
    lines = []
    if not r['ok']:
        lines.append(f"  {fail('✘')} {r['domain']} — {r.get('error', 'unknown error')}")
        return lines
    days = r.get('days_left', 999)
    icon = ok('✔') if days > 30 else warn('⚠') if days > 7 else fail('✘')
    exp_str = r.get('expiry', 'Unknown')[:10]
    lines.append(f"  {icon} {bold(r['domain'])}")
    lines.append(f"     Expires:     {exp_str} ({days} days)")
    if r.get('registrar'):
        lines.append(f"     Registrar:   {r['registrar']}")
    if r.get('nameservers'):
        lines.append(f"     Name Servers:{', '.join(r['nameservers'][:4])}")
    return lines

def format_ssl_brief(r):
    h = r['hostname']
    if not r['ok']:
        return [f"  {fail('✘')} {h} — {r['errors'][0][1]}"]
    days = r['cert']['days_left']
    grade = r['grade']
    icon = ok('✔') if days > 30 else warn('⚠') if days > 7 else fail('✘')
    g_color = ok(grade) if grade in ('A','B') else warn(grade) if grade == 'C' else fail(grade)
    return [f"  {icon} {h} — Grade {g_color} — {days}d remaining"]

# ─────────────────────────────────────────────
# HTML/JSON report generators
# ─────────────────────────────────────────────
def generate_html_report(results, title="EdgeIQ SSL & Domain Watcher Report"):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
  body{{font-family:system-ui;background:#0b0f14;color:#e8eef7;padding:40px;}}
  h1{{color:#3dd9ff;}}
  .grade{{font-weight:900;font-size:1.4em;}}
  .grade-A{{color:#70f0a8;}} .grade-B{{color:#a8f070;}}
  .grade-C{{color:#f0c070;}} .grade-D{{color:#f07070;}} .grade-F{{color:#ff4444;}}
  .card{{background:#121923;border:1px solid #233142;border-radius:12px;padding:18px;margin:12px 0;}}
  .ok{{color:#70f0a8;}} .warn{{color:#f0c070;}} .fail{{color:#ff7070;}}
  table{{width:100%;border-collapse:collapse;}}
  td{{padding:6px 12px;border-bottom:1px solid #233142;}}
  .param{{color:#9fb0c7;font-size:0.85em;}}
</style></head><body>
<h1>{title}</h1>
<p>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>"""
    for r in results:
        if not r.get('ok'): continue
        h = r['hostname']
        g = r['grade']
        days = r['cert']['days_left']
        html += f"""<div class="card">
<h3>{h} <span class="grade grade-{g}">{g}</span> — {days}d left</h3>
<table>
<tr><td class="param">Issuer</td><td>{r['cert']['issuer']}</td></tr>
<tr><td class="param">Valid</td><td>{r['cert']['not_before'][:10]} → {r['cert']['not_after'][:10]}</td></tr>
<tr><td class="param">Protocol</td><td>{r['protocols'][0]}</td></tr>
<tr><td class="param">Cipher</td><td>{r['cipher']['name']}</td></tr>"""
        for hdr, val in r.get('security_headers', {}).items():
            status = '✔' if val != '(not set)' else '✘'
            html += f"<tr><td class=\"param\">{status} {hdr}</td><td>{val}</td></tr>"
        html += "</table></div>"
    html += "</body></html>"
    return html

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def build_parser():
    p = argparse.ArgumentParser(description='EdgeIQ SSL & Domain Expiry Watcher')
    p.add_argument('--domain', help='Single domain to check')
    p.add_argument('--domains', nargs='+', help='Multiple domains')
    p.add_argument('--warn-days', type=int, default=30, help='Expire warning threshold (default: 30)')
    p.add_argument('--verbose', '-v', action='store_true', help='Full output')
    p.add_argument('--brief', '-b', action='store_true', help='Brief one-line output')
    p.add_argument('--check-http', action='store_true', help='Fetch security headers (HTTP reachability check)')
    p.add_argument('--no-http', action='store_true', help='Skip HTTP reachability check')
    p.add_argument('--port-scan', action='store_true', help='Quick port scan on common security ports')
    p.add_argument('--output-json', help='Write JSON report')
    p.add_argument('--output-html', help='Write HTML report')
    p.add_argument('--silent', action='store_true', help='Only show warnings')
    p.add_argument('--no-color', action='store_true', help='Strip ANSI color codes')
    p.add_argument('--timeout', type=int, default=10, help='Connection timeout (default: 10s)')
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    domains = []
    if args.domain: domains.append(args.domain)
    if args.domains: domains.extend(args.domains)

    if not domains:
        parser.print_help()
        sys.exit(0)

    # Global flags
    NO_COLOR = args.no_color
    def c(text, color): return text if NO_COLOR else color + text + _RST

    # ── License gate (features that require Pro/Bundle) ──
    gated = []
    # Security header analysis requires check_http flag explicitly set
    if args.check_http and not is_pro():
        gated.append("Security Header Analysis")
    if args.port_scan and not is_pro():
        gated.append("Port Scanning")
    if args.output_html and not is_pro():
        gated.append("HTML Report Export")
    if args.output_json and not is_pro():
        gated.append("JSON Report Export")

    if gated:
        print()
        print(f"{fail('╔' + '═'*58 + '╗')}")
        print(f"{fail('║')}  {'🔒 Pro / Bundle Feature(s) Required':^54}  {fail('║')}")
        print(f"{fail('╠' + '═'*58 + '╣')}")
        for feat in gated:
            print(f"{fail('║')}    ✘ {feat:<51}  {fail('║')}")
        print(f"{fail('╠' + '═'*58 + '╣')}")
        print(f"{fail('║')}  Your current tier: FREE{' '*43}  {fail('║')}")
        print(f"{fail('║')}  Upgrade options:{' '*46}  {fail('║')}")
        print(f"{fail('║')}    Pro ($9/mo):    https://buy.stripe.com/7sYaEZeCn5934nW8AE7wA01  {fail('║')}")
        print(f"{fail('║')}    Bundle ($39/mo): https://buy.stripe.com/aFabJ3am79pjg6E18c7wA02  {fail('║')}")
        print(f"{fail('╚' + '─'*58 + '╝')}")
        print()
        sys.exit(1)

    results = []

    # ── header ──
    if not args.silent:
        print(f"\n{c(bold('╔══════════════════════════════════════════╗'), _CYA)}")
        print(f"{c(bold('║   EdgeIQ SSL & Domain Watcher            ║'), _CYA)}")
        print(f"{c(bold('╚══════════════════════════════════════════╝'), _CYA)}\n")

    for domain in domains:
        h = domain.replace('https://','').replace('http://','').split('/')[0].split(':')[0]

        if not args.silent:
            print(f"{c('▶', _MAG)} Scanning {bold(h)}")

        # SSL scan
        ssl_r = fetch_ssl_full(h, 443, timeout=args.timeout,
                               check_http=not args.no_http)
        results.append(ssl_r)

        if args.verbose:
            for line in format_ssl_verbose(ssl_r): print(line)
        elif args.brief or args.silent:
            for line in format_ssl_brief(ssl_r): print(line)
        else:
            # Default: brief
            for line in format_ssl_brief(ssl_r): print(line)

        # Port scan
        if args.port_scan:
            if not args.silent:
                print(f"  {c('◌', _CYA)} Checking common ports...")
            open_p = quick_port_check(h)
            if open_p:
                port_names = [f"{p}({COMMON_PORTS[p]})" for p in open_p if p in COMMON_PORTS]
                print(f"  {c('✔', _GRN)} Open: {', '.join(port_names)}")
            else:
                print(f"  {c('✘', _RED)} No common ports open")

        # WHOIS domain check
        dom_r = fetch_domain_expiry(h, args.warn_days)
        results.append(dom_r)

        if args.verbose:
            for line in format_domain_verbose(dom_r): print(line)
        elif not args.silent:
            dom_days = dom_r.get('days_left')
            if dom_days is not None:
                icon = ok('✔') if dom_days > 30 else warn('⚠') if dom_days > 7 else fail('✘')
                print(f"  {icon} Domain expires: {dom_r['expiry'][:10]} ({dom_days}d)")
            else:
                print(f"  {warn('⊘')} WHOIS: {dom_r.get('error','unavailable')}")

        print()

    # ── summary ──
    ssl_ok   = [r for r in results if r.get('grade') in ('A','B','C')]
    ssl_warn = [r for r in results if r.get('grade') == 'D']
    ssl_fail = [r for r in results if r.get('grade') == 'F']
    dom_warn = [r for r in results if r.get('warn')]

    if not args.silent:
        print(f"{c('─', _CYA) * 42}")
        print(f"  Summary: {len(ssl_ok)} OK | {len(ssl_warn)} Warning | {len(ssl_fail)} Fail | {len(dom_warn)} domain alerts")

    # JSON export
    if args.output_json:
        out = {
            'generated': datetime.now(timezone.utc).isoformat(),
            'warn_days': args.warn_days,
            'results': [{'hostname': r.get('hostname'), 'ok': r.get('ok'),
                         'grade': r.get('grade'), 'cert': r.get('cert'),
                         'errors': r.get('errors'), 'scan_time': r.get('scan_time')}
                        for r in results]
        }
        with open(args.output_json, 'w') as f:
            json.dump(out, f, indent=2, default=str)
        print(f"\n  {c('✔ JSON report →', _GRN)} {args.output_json}")

    # HTML export
    if args.output_html:
        with open(args.output_html, 'w') as f:
            f.write(generate_html_report(results))
        print(f"\n  {c('✔ HTML report →', _GRN)} {args.output_html}")

    # Exit code: 0 = clean, 1 = warnings
    sys.exit(1 if (ssl_warn or ssl_fail or dom_warn) else 0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda *a: (print('\nAborted.'), sys.exit(2)))
    main()