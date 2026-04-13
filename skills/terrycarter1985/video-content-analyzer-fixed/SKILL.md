# Video Content Analyzer - ClawHub Skill

Analyze video content, extract keyframes, search web for references, store metadata in Supabase, and generate Feishu Wiki reports.

## Description

This skill provides a complete video content analysis workflow that automatically processes video files, extracts meaningful frames at configurable intervals, performs web searches for content references, stores all metadata and results in Supabase, and publishes professional analysis reports directly to Feishu Wiki.

## Quick Start

```claw
# Install the skill
clawhub install video-content-analyzer

# Process a video file
CALL video-content-analyzer:process_video(
    video_path="/path/to/your/video.mp4",
    user_id="user-uuid-here",
    space_id="feishu-wiki-space-id"
)
```

## Use Cases

- **Content Creators**: Automatically document and reference sources in video content
- **Media Analysis**: Process and catalog video libraries with searchable metadata
- **Education**: Generate indexed study materials from lecture recordings
- **Compliance**: Create audit trails for video content with source references

## Features

| Feature | Status |
|---------|--------|
| Video frame extraction at 10s intervals | ✅ |
| Google Custom Search API integration | ✅ |
| Supabase metadata storage | ✅ |
| Feishu Wiki report generation | ✅ |
| ffmpeg video probing | ✅ |
| Type coercion & error handling | ✅ v1.0.1 |
| Auto user profile creation | ✅ v1.0.1 |
| Feishu-compatible link rendering | ✅ v1.0.1 |

## Methods

### process_video(video_path, user_id, space_id)

Main entry point for video analysis workflow.

**Parameters:**
- `video_path` (string, required): Local path to the input video file
- `user_id` (string, required): UUID of the user (for Supabase RLS)
- `space_id` (string, required): Feishu Wiki space ID for publishing

**Workflow:**
1. Probe video and extract metadata (duration, resolution, FPS)
2. Create video asset record in Supabase
3. Extract keyframes at 10-second intervals
4. Save frames to filesystem and database
5. Perform web search for frame content references
6. Store search results with relevance scoring
7. Generate structured analysis report
8. Publish to Feishu Wiki with proper link formatting
9. Update video status to "processed"

## Environment Variables

Required in `.env`:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Google Custom Search
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Feishu/Lark
FEISHU_APP_ID=cli-your-app-id
FEISHU_APP_SECRET=your-app-secret

# Optional
FRAMES_OUTPUT_DIR=./extracted_frames
```

## Database Schema

See `supabase/migrations/` for complete schema.

- `video_assets`: Main video records with metadata
- `video_frames`: Extracted frames with timestamps and OCR content
- `search_results`: Google search references per frame
- `wiki_pages`: Generated wiki page records
- `profiles`: User profiles for RLS

## Release Notes

### v1.0.1
- **FIX**: Feishu Wiki search references now render correctly
- **FIX**: Supabase metadata storage issues resolved
- **FIX**: Video metadata fallback handling for edge cases
- **IMPROVE**: Added comprehensive logging

### v1.0.0
- Initial release with core functionality
