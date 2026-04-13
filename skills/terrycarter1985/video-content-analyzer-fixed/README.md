# Video Content Analysis Workflow

An integrated workflow for processing video content, extracting keyframes, searching for related information, storing results in Supabase, and publishing documentation to Feishu Wiki.

## Features

- **Video Frame Extraction**: Extract keyframes at configurable intervals using ffmpeg
- **Content Search**: Automatically search the web for information related to frame content
- **Database Storage**: All metadata and results stored in Supabase Postgres database
- **Wiki Publishing**: Auto-generate analysis reports and publish directly to Feishu Wiki
- **Extensible**: Built as a ClawHub skill for easy extension and integration with other tools

## Tech Stack

- **Video Processing**: ffmpeg-python
- **Database**: Supabase (Postgres + Auth + Storage)
- **Search**: Google Custom Search API
- **Wiki**: Feishu OpenAPI
- **Language**: Python 3.10+

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy environment file and fill in credentials:
   ```bash
   cp .env.example .env
   ```

3. Set up Supabase schema:
   ```bash
   # Install Supabase CLI first
   supabase db push
   ```

## Changelog

### v1.0.1 (April 2026)

**Bug Fixes:**
- 🐛 **Feishu Wiki Links**: Fixed search reference links not rendering correctly. Now uses Feishu-compatible format with explicit URLs
- 🐛 **Supabase Storage**: Fixed metadata not saving due to:
  - Auto-creating user profiles if they don't exist
  - Type coercion for numeric fields (prevents None value errors)
  - Proper exception handling and logging
- 🐛 **Video Metadata**: Fixed duration/frame count fallback handling for files with missing stream data

**Improvements:**
- Added comprehensive logging for all database operations

## Usage

```bash
python src/main.py path/to/your/video.mp4 --user-id <your-user-uuid> --space-id <feishu-wiki-space-id>
```

## Workflow

1. **Upload/Input Video**: Provide path to video file
2. **Extract Keyframes**: System extracts frames at 10-second intervals
3. **Analyze Content**: (Optional) Run OCR/vision models on frames
4. **Web Search**: Search for related information about frame content
5. **Store Results**: Save all data to Supabase database
6. **Generate Report**: Create structured analysis report
7. **Publish**: Push report to Feishu Wiki

## ClawHub Skill

This tool is published as a ClawHub skill. Install it with:
```bash
clawhub install video-analysis-workflow
```

## License

MIT