---
name: file-backup-organizer
description: |
  Intelligent file backup and organizer. Recursively scans folders, categorizes files by type, supports filtering/exclusion, handles duplicates, and generates detailed reports.

  Triggers:
  - User asks to backup a folder
  - User asks to organize/sort files by type
  - User mentions WeChat file cleanup, file archiving, file sorting
  - User says "backup files", "organize folder", "sort files", "clean up files"
  - User wants to exclude specific file types during backup
metadata:
  openclaw:
    emoji: "[BACKUP]"
---

# file-backup-organizer v1.0.0 -- Intelligent File Backup & Organizer

## Core Functions

| Feature | Description |
|---------|-------------|
| **Recursive Scan** | Scans source folder and all subdirectories |
| **Smart Categorization** | Auto-classifies by extension (Word, Excel, PDF, Images, etc.) |
| **Flexible Filtering** | Supports excluding specific file types (e.g. .tmp, .log, .cache) |
| **Duplicate Handling** | Auto-appends sequential numbers to avoid overwriting |
| **Detailed Reports** | Generates backup inventory and deletion lists |
| **Risk Warnings** | Flags files that may break without directory structure |

## How to Use

The main script is `scripts/backup_files.py`. It provides Python functions:

```python
from scripts.backup_files import backup_files, organize_by_type
```

### backup_files(source_path, exclude_extensions=None)
- `source_path`: Source folder path (e.g. "D:\\Projects")
- `exclude_extensions`: List of extensions to exclude (e.g. [".tmp", ".log"])
- Returns: dict with success status, file counts, categories, backup directory

### organize_by_type(source_path)
- `source_path`: Source folder path
- Returns: same as backup_files (without exclusion)

## Execution

Run via Python:
```bash
python scripts/backup_files.py
```

Or import and call functions directly in your workflow.

## Supported File Types

| Category | Extensions |
|----------|-----------|
| Word | .doc, .docx, .docm, .odt, .rtf |
| Excel | .xls, .xlsx, .xlsm, .csv, .ods |
| PDF | .pdf |
| PPT | .ppt, .pptx, .pptm, .ppsx |
| Images | .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg, .psd |
| Videos | .mp4, .avi, .mkv, .mov |
| Audio | .mp3, .wav, .flac |
| Archives | .zip, .rar, .7z |
| Code | .py, .js, .html, .css, .java, .cpp, .php, .json, .xml |
| Text | .txt, .md, .log |

## Output

Backup creates a folder named `{source}_backup` with:
- Subfolders per file type
- `backup_report.txt` -- full inventory with file counts and names
- `exclusion_list.txt` -- list of excluded files (only if exclude_extensions used)

## Warnings

These file types may break without original directory structure:
- Web files: .html, .htm, .css, .js
- Server scripts: .php, .asp, .aspx, .jsp
- Config files: .json, .xml, .yaml, .ini

Such files are flagged in the backup report.

## Dependencies

None -- uses Python standard library only (os, shutil, pathlib, collections, datetime).
