# sppb5.php — Available Actions

Custom PHP endpoint for direct DB and file access. All requests require `X-Falang-Token` header.

## Read Actions (GET)

| Action | Params | Returns |
|--------|--------|---------|
| `purge_cache` | — | `{ok, cleared, errors}` |
| `ext_params` | `ext_id=N` | `{ok, params: "json string"}` |
| `slice` | `id=N&from=N&len=N` | `{slice: "..."}` — substring of SP Builder JSON |
| `find_all` | `id=N&q=string` | `{count, positions:[]}` — all occurrences in SP Builder JSON |
| `select_query` | POST body: `{sql}` | `{ok, rows:[]}` — SELECT only, `##` replaced with table prefix |
| `update_jmap_source` | `id=N&published=0\|1` | `{ok, rows}` — enable/disable JSitemap source |
| `set_plugin_enabled` | `ext_id=N&enabled=0\|1` | `{ok, rows}` |
| `set_falang_qacache` | `ext_id=N` (default 10140) | `{ok, rows, params_preview}` |

## Write Actions (POST with JSON body)

| Action | Body | Returns |
|--------|------|---------|
| `replace_text_field` | `{id, uid, new_text, search_from}` | `{ok, uid_pos, old_preview, new_preview, rows}` |
| `set_ext_params` | `{ext_id, params: "json string"}` | `{ok, rows}` |
| `update_jmap_source_params` | `{id, params: "json string"}` | `{ok, rows}` |
| `patch_config` | `{patches: [{label, pattern, replacement}]}` | `{ok, applied:[]}` — regex patches on configuration.php |
| `select_query` | `{sql}` | `{ok, rows:[]}` |

## Table Prefix Substitution

In `select_query` SQL, use `##` as table prefix placeholder — it gets replaced with the actual prefix (e.g., `bwhwo_`).

```sql
SELECT * FROM ##extensions WHERE type='plugin' AND enabled=1
```

## Deploying New Actions

When a needed action doesn't exist, add it via SFTP by editing `sppb5.php`. Insert new `if ($action === '...') { ... exit; }` blocks before the final `echo json_encode(['error'=>'unknown action'])` line. After deploying, call `purge_cache` to clear PHP opcode cache so the new action is recognized.
