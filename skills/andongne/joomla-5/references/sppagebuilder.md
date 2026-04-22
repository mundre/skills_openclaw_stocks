# SP Page Builder — Direct Content Editing

## Overview

SP Builder stores page content as a large JSON blob in `##sppagebuilder.content`. Each addon (block) has a unique UID. The `sppb5.php` endpoint allows direct edits without going through the Joomla backend.

## Finding Content

```python
# Find all occurrences of a string in a page's JSON
sppb('find_all', '&id=173&q=TCF+Canada')
# → {count: N, positions: [pos1, pos2, ...]}

# Inspect content at a position
sppb('slice', '&id=173&from=96029&len=400')
# → {slice: "...json fragment..."}
```

## Editing a Text Field

```python
sppb('replace_text_field', body={
    'id': 173,           # SP Builder record ID
    'uid': '59e0eb11-0eda-447b-812b-abc14a08b564',  # addon UID
    'new_text': 'New content here',
    'search_from': 90000  # MUST be before uid position, not after
})
```

> ⚠️ `search_from` must be **before** the UID position in the JSON. The script scans forward from `search_from` to find the UID, then finds the first `"text":"` field after it.

> ⚠️ If a UID appears multiple times (e.g. mobile and desktop variants), use `find_all` first to identify positions, then set `search_from` to target the correct occurrence.

## Emoji Encoding

Gandi's WAF/Varnish blocks requests containing 4-byte UTF-8 (emoji) or JSON surrogates. Use HTML entities:

```python
E_ARROW  = "&#10148;"        # ➤
E_MAPLE  = "&#127809;"       # 🍁
E_FLEUR  = "&#9884;&#65039;" # ⚜️
E_LAPTOP = "&#128187;"       # 💻
E_PAPER  = "&#128196;"       # 📄
```

## FaLang Translations for SP Builder

Translations for SP Builder addons use `reference_table=sppagebuilder` and `reference_id=<addon UID>` (the UUID string, not the numeric record ID).

```python
# Inject/update ZH translation via FaLang inject endpoint
import urllib.request, urllib.parse, os

FALANG_URL = os.environ['FALANG_INJECT_URL']  # /falang-inject/index.php
TOKEN = os.environ['FALANG_SECRET_TOKEN']

data = urllib.parse.urlencode({
    'reference_table': 'sppagebuilder',
    'reference_id': '<addon-uid>',
    'reference_field': 'text',
    'language_id': 4,  # zh-CN
    'value': '中文内容',
    'modified_by': 898,
}).encode()
req = urllib.request.Request(FALANG_URL, data=data,
    headers={'X-Falang-Token': TOKEN, 'Content-Type': 'application/x-www-form-urlencoded'})
with urllib.request.urlopen(req) as r:
    print(r.read())
```

## Mandatory: Purge Cache After Edits

SP Builder renders are cached. Without purge, the frontend shows stale content even after DB update.

```python
sppb('purge_cache')
```
