# Joomla 5 — SEO Reference

## JSitemap Pro

Component: `com_jmap` (extension_id varies). Config stored in `##extensions.params` as JSON.

### Key global params

| Param | Recommended | Notes |
|-------|-------------|-------|
| `disable_priority` | `"0"` | Enable `<priority>` tags |
| `disable_changefreq` | `"0"` | Enable `<changefreq>` tags |
| `advanced_multilanguage` | `"1"` | Enable hreflang generation |
| `sitemap_links_sef` | `"1"` | Use SEF URLs in sitemap |

### Sources table (`##jmap`)

Each row is a sitemap source (content, menu, user-defined).  
Params per source: `{xmlinclude, priority, changefreq, hreflanginclude, ...}`

```python
# Read params
sppb('ext_params', f'&ext_id={JMAP_EXT_ID}')

# Update global params
params['disable_priority'] = '0'
sppb('set_ext_params', body={'ext_id': JMAP_EXT_ID, 'params': json.dumps(params)})

# Disable a source (e.g. SP Page Builder generates duplicate /component/ URLs)
sppb('update_jmap_source', '&id=41&published=0')

# Set per-source priority/changefreq
sppb('update_jmap_source_params', body={'id': 2, 'params': json.dumps({
    'xmlinclude': '1', 'priority': '0.8', 'changefreq': 'weekly', 'hreflanginclude': '1'
})})
```

### Sitemap URL

JSitemap Pro's sitemap is accessible at:
`/index.php?option=com_jmap&view=sitemap&format=xml`

To expose `/sitemap.xml`, add to `.htaccess` inside `<IfModule mod_rewrite.c>` **before** the SEF catchall:
```apache
RewriteRule ^sitemap\.xml$ /index.php?option=com_jmap&view=sitemap&format=xml [R=301,L]
```
> A transparent rewrite (without `R=301`) fails because Joomla reads `REQUEST_URI` for routing — it sees `/sitemap.xml` and returns 404. The 301 makes the browser/crawler send a new request with the correct URI.

### Common sitemap issues

- **`/component/sppagebuilder/` URLs** — SP Page Builder source generates non-canonical URLs. Disable source id in `##jmap` where `type='user' AND name LIKE '%page builder%'`.
- **No `<priority>`/`<changefreq>`** — Set `disable_priority: "0"` and `disable_changefreq: "0"` in global params.
- **Missing hreflang** — Requires language associations in Joomla (separate menu items per language). FaLang session-based switching does not generate hreflang-capable separate URLs.

## robots.txt

Standard additions for Joomla:
```
Disallow: /component/
Disallow: /administrator/
Sitemap: https://example.org/sitemap.xml
```

## Canonical Tags

Joomla 5 + Helix Ultimate: avoid double canonical. Add canonical programmatically in template `index.php`:
```php
$doc = Factory::getDocument();
$doc->addCustomTag('<link rel="canonical" href="' . Uri::current() . '" />');
```
Remove any hardcoded canonical in the template HTML.

## hreflang

With FaLang session-based switching (no separate language URLs), add static hreflang to template:
```php
$doc->addHeadLink(Uri::base(), 'alternate', 'rel', ['hreflang' => 'fr']);
$doc->addHeadLink(Uri::base(), 'alternate', 'rel', ['hreflang' => 'zh-Hans']);
$doc->addCustomTag('<link href="' . Uri::base() . '" rel="alternate" hreflang="x-default" />');
```

For proper `/zh/[slug]` crawlable URLs (full hreflang):
1. Change menu items from `language=*` to `language=fr-FR`
2. Create mirror menu items with `language=zh-CN`
3. Add language associations (FR ↔ ZH) in Joomla
4. Language Filter plugin (already enabled) generates `/zh/[slug]` routes automatically
5. FaLang translates content at those routes (translations already in `##falang_content`)
