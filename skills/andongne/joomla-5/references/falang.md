# FaLang — Multilingual Architecture

## How FaLang Works

FaLang translates content by replacing DB query results at runtime via a custom DB driver (`falangdriver` plugin). It does **not** create separate URLs per language by default.

- Translations stored in `##falang_content` (fields: `reference_table`, `reference_id`, `reference_field`, `language_id`, `value`)
- Language switching via session cookie (mod_falang module + falangcf plugin)
- `/zh/` = special URL that sets the ZH session and reloads the homepage — not a URL prefix for all pages

## Plugin Stack

| Plugin | Role |
|--------|------|
| `falangdriver` | DB driver override — injects translations into query results |
| `falangcf` | Cookie/fragment language detection |
| `falangquickjump` | Admin UI helper |
| `mod_falang` | Frontend language switcher module |

## Querying Translations

```sql
-- Count translations per table for language_id=4 (zh-CN)
SELECT reference_table, COUNT(*) as cnt FROM ##falang_content WHERE language_id=4 GROUP BY reference_table

-- Get ZH translation of a menu item title
SELECT fc.value FROM ##falang_content fc
WHERE fc.reference_table='menu' AND fc.reference_id=101
AND fc.reference_field='title' AND fc.language_id=4
```

## Language IDs (typical)

| ID | Code | Language |
|----|------|----------|
| 3 | fr-FR | French |
| 4 | zh-CN | Chinese Simplified |

## URL Routing for Crawlable ZH Pages

FaLang session-based switching = same URL for FR and ZH → Google only indexes FR version.

**To get crawlable `/zh/[slug]` URLs:**
1. Requires Joomla's **Language Filter** plugin (usually already active)
2. Change existing menu items from `language=*` → `language=fr-FR`
3. Create duplicate menu items with `language=zh-CN` (same link target)
4. Add language associations between FR and ZH items
5. Language Filter auto-generates `/zh/[slug]` routes
6. FaLang serves translated content at those routes

> This is the official FaLang recommendation (source: faboba.com/composants/falang/documentation). FaLang does not have its own URL-prefix routing — it relies on Joomla's native Language Filter.

## FaLang Performance

Enable query caching to reduce DB overhead:
```python
sppb('set_falang_qacache', '&ext_id=10140')
# Sets: qacaching=1, update_caching=1
```

Or manually in `##extensions.params` for `com_falang`:
```json
{"qacaching": "1", "update_caching": "1"}
```

## Varnish Conflict

FaLang's session cookie (`falangcf` plugin) is set on **every anonymous page load**. Combined with Joomla's `Cache-Control: no-store`, this prevents Varnish from caching any pages. The only architectural fix is URL-based language routing (see above), which eliminates the need for session cookies on anonymous requests.
