---
name: joomla-5
description: "Joomla 5 site management via REST API, SFTP, and direct database access. Use when working with a Joomla 5 site to: manage articles, categories, menus, and modules via the REST API; edit files via SFTP (templates, .htaccess, robots.txt, configuration.php); run DB queries or patches via a custom PHP endpoint; configure SEO (sitemap, canonical, hreflang, robots.txt); tune performance (gzip, cache, session handler, Varnish); manage extensions and plugins; work with SP Page Builder content; configure FaLang multilingual translations; configure JSitemap Pro; or diagnose Core Web Vitals issues."
---

# Joomla 5 — Site Management

## Access Patterns

Three complementary access layers — choose the right one for each task:

| Layer | Use for | Tool |
|-------|---------|------|
| **REST API** | Articles, categories, menus (read/write) | `urllib` / `requests` |
| **SFTP** | Template files, .htaccess, configuration.php, robots.txt | `paramiko` |
| **DB endpoint** (sppb5.php) | Direct DB queries, extension params, plugin config, cache purge | `urllib` |

> ⚠️ **Never use `curl --noproxy '*'`** in this sandbox — it errors. Always use Python `urllib`.

> ⚠️ **configuration.php is chmod 444** — use SFTP `chmod(0o644)` before write, restore `0o444` after.

## REST API

Base: `$JOOMLA_BASE_URL/api/index.php/v1/`  
Auth: `Authorization: Bearer $JOOMLA_API_TOKEN`

```python
import urllib.request, json, os

BASE = os.environ['JOOMLA_BASE_URL']
TOKEN = os.environ['JOOMLA_API_TOKEN']

def api(method, path, body=None):
    url = f"{BASE}/api/index.php/v1/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={'Authorization': f'Bearer {TOKEN}',
                 'Accept': 'application/vnd.api+json',
                 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

Key endpoints:
- `content/articles` — list/create articles
- `content/articles/{id}` — read/update/delete
- `content/categories` — categories
- `menus/{menutype}/items` — menu items
- `extensions?filter[type]=plugin` — list extensions

## SFTP Access

```python
import paramiko, os

def sftp_connect():
    key = paramiko.Ed25519Key.from_private_key_file(os.environ['GANDI_SSH_KEY'])
    t = paramiko.Transport((os.environ['GANDI_SFTP_HOST'], 22))
    t.connect(username=os.environ['GANDI_SFTP_USER'], pkey=key)
    return paramiko.SFTPClient.from_transport(t), t

sftp, transport = sftp_connect()
# Read
with sftp.open('/path/to/file', 'r') as f: content = f.read().decode()
# Write (for read-only files: chmod first)
sftp.chmod('/path/to/configuration.php', 0o644)
with sftp.open('/path/to/configuration.php', 'w') as f: f.write(new_content)
sftp.chmod('/path/to/configuration.php', 0o444)
```

## DB Endpoint (sppb5.php)

Custom PHP endpoint at `/falang-inject/sppb5.php`. Auth: `X-Falang-Token` header.  
See `references/sppb5-actions.md` for all available actions.

```python
import urllib.request, json, os

SPPB = os.environ['SPPB_URL']   # https://site.org/falang-inject/sppb5.php
TOKEN = os.environ['FALANG_SECRET_TOKEN']

def sppb(action, params='', body=None):
    url = f"{SPPB}?action={action}{params}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data,
        headers={'X-Falang-Token': TOKEN,
                 **(({'Content-Type': 'application/json'}) if body else {})})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

Quick actions:
```python
sppb('purge_cache')                                    # purge Joomla file cache
sppb('ext_params', '&ext_id=10156')                   # read extension params
sppb('set_plugin_enabled', '&ext_id=123&enabled=0')   # disable plugin
sppb('select_query', body={'sql': 'SELECT ...'})       # read-only DB query
```

## SEO Configuration

See `references/seo.md` for detailed SEO workflows covering:
- Sitemap XML (JSitemap Pro)
- robots.txt
- Canonical tags
- hreflang / FaLang multilingual
- Core Web Vitals / TTFB

## SP Page Builder

See `references/sppagebuilder.md` for direct content editing patterns.

## FaLang Multilingual

See `references/falang.md` for translation and URL routing architecture.

## Performance / TTFB

See `references/performance.md` for cache, gzip, session, and Varnish analysis.
