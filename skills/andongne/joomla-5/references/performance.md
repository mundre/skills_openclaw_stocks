# Joomla 5 — Performance & TTFB

## Diagnosis Checklist

```python
# 1. Measure TTFB
import urllib.request, time
t0 = time.time()
with urllib.request.urlopen('https://site.org/', timeout=10) as r:
    h = dict(r.headers); r.read()
print(f"TTFB: {round((time.time()-t0)*1000)}ms | X-Cache: {h.get('X-Cache')} | Set-Cookie: {'Set-Cookie' in h}")

# 2. Check gzip
req = urllib.request.Request('https://site.org/', headers={'Accept-Encoding': 'gzip'})
with urllib.request.urlopen(req) as r:
    print(r.headers.get('Content-Encoding'))  # should be 'gzip'
```

## Varnish Not Caching

Symptom: `X-Cache: MISS` on every request, `Age: 0`.

Causes (check in order):

1. **`Set-Cookie` in response** — Varnish bypasses cache for all responses that set cookies. Joomla always sets a session cookie for anonymous users.
2. **`Cache-Control: no-store`** — Joomla sends this by default.

Root cause: FaLang creates a session for every visitor to track language preference. As long as session-based language switching is in use, Varnish cannot cache pages on Gandi's managed infrastructure.

**Workaround**: URL-based language routing (separate `/zh/[slug]` routes) eliminates language cookies → Varnish can cache.

## configuration.php Tunable Params

Edit via SFTP (chmod 444→644→444):

| Param | Recommended | Effect |
|-------|-------------|--------|
| `gzip` | `true` | HTML compression (~85% reduction) |
| `session_handler` | `filesystem` | Removes 1 DB write per request |
| `session_metadata` | `false` | Reduces session storage overhead |
| `cachetime` | `60` | Less frequent cache regeneration (minutes) |
| `cache_handler` | `file` | Keep as-is (file cache is fast) |

## Plugins to Disable (low value, high overhead)

| Element | ext_id (typical) | Reason |
|---------|----------|--------|
| `jooa11y` | varies | Accessibility overlay — not needed in production |
| `stats` | varies | Pings Joomla.org on admin visits |

```python
sppb('set_plugin_enabled', f'&ext_id={ext_id}&enabled=0')
```

## FaLang Query Cache

```python
sppb('set_falang_qacache')  # enables qacaching + update_caching
```

Caches translated DB query results in Joomla's file cache. Significant reduction in FaLang overhead for pages with many translatable elements.

## Cache Purge

Always purge after configuration changes:
```python
sppb('purge_cache')
```

Clears `/cache/` and `/administrator/cache/` (preserves `index.html` files).

## Core Web Vitals — Mobile LCP

If mobile LCP > 2.5s:
1. Check TTFB — high TTFB cascades to LCP
2. Identify LCP element (typically hero image or above-fold SP Builder block)
3. Add `<link rel="preload" as="image" href="...">` in template `<head>` for the LCP image
4. Ensure LCP image has explicit `width`/`height` attributes (prevents layout shift)
5. Convert hero images to WebP format (significant size reduction)
