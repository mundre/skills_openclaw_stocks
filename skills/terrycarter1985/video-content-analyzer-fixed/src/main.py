#!/usr/bin/env python3
"""
Video Content Analysis & Documentation Workflow
Integrates video frame extraction, web search, database storage, and wiki publishing
"""
import os
import uuid
from dotenv import load_dotenv
from modules.video_processor import VideoProcessor
from modules.search_client import SearchClient
from modules.database_client import DatabaseClient
from modules.feishu_wiki_client import FeishuWikiClient

# Load environment variables
load_dotenv()

class VideoAnalyzer:
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.search_client = SearchClient()
        self.db_client = DatabaseClient()
        self.wiki_client = FeishuWikiClient()
        
        self.frames_output_dir = os.getenv("FRAMES_OUTPUT_DIR", "./extracted_frames")
        os.makedirs(self.frames_output_dir, exist_ok=True)
    
    def process_video(self, video_path: str, user_id: str, space_id: str) -> dict:
        """
        Full video processing workflow:
        1. Extract keyframes
        2. Store metadata in database
        3. Search for frame content information
        4. Generate wiki page with findings
        5. Publish to Feishu Wiki
        """
        video_filename = os.path.basename(video_path)
        file_size = os.path.getsize(video_path)
        
        # Step 1: Get video info and save to database
        video_info = self.video_processor.get_video_info(video_path)
        video_id = self.db_client.save_video_asset(
            user_id=user_id,
            filename=video_filename,
            storage_path=video_path,
            duration=video_info.duration_seconds,
            file_size=file_size
        )
        
        print(f"Created video record: {video_id}")
        
        # Step 2: Extract keyframes
        print(f"Extracting keyframes from {video_filename}...")
        frames = self.video_processor.extract_keyframes(video_path, interval_seconds=10)
        print(f"Extracted {len(frames)} frames")
        
        # Step 3: Process each frame
        processed_frames = []
        frame_ids = []
        
        for i, frame in enumerate(frames):
            print(f"Processing frame {i+1}/{len(frames)}...")
            
            # Save frame to storage
            frame_filename = f"{video_id}_frame_{frame.frame_number:06d}.jpg"
            frame_path = os.path.join(self.frames_output_dir, frame_filename)
            self.video_processor.save_frame(frame, frame_path)
            
            # Save frame record to database
            frame_id = self.db_client.save_frame(
                video_id=video_id,
                frame_number=frame.frame_number,
                timestamp=frame.timestamp_seconds,
                storage_path=frame_path,
                width=frame.width,
                height=frame.height,
                content_tags=[]  # Would be populated by OCR/vision model in production
            )
            frame_ids.append(frame_id)
            
            # Step 4: Search for related information (using mock query for demo)
            # In production, this would use OCR/vision model output as search query
            search_query = f"reference information for frame content"
            search_results = self.search_client.search_image_content(search_query, num_results=3)
            
            # Save search results
            self.db_client.save_search_results(frame_id, search_query, search_results)
            
            processed_frames.append({
                "frame_id": frame_id,
                "timestamp": frame.timestamp_seconds,
                "frame_path": frame_path,
                "content_tags": [],
                "search_results": [r.__dict__ for r in search_results]
            })
        
        # Step 5: Generate and publish wiki page
        print("Generating wiki page...")
        wiki_title = f"Video Analysis: {video_filename}"
        wiki_content = self.wiki_client.generate_page_content(video_filename, processed_frames)
        
        # Save wiki page record
        wiki_id = self.db_client.save_wiki_page(
            user_id=user_id,
            title=wiki_title,
            content=wiki_content,
            video_id=video_id,
            frame_ids=frame_ids
        )
        
        # Publish to Feishu Wiki
        print("Publishing to Feishu Wiki...")
        wiki_page = self.wiki_client.create_page(
            space_id=space_id,
            title=wiki_title,
            content=wiki_content
        )
        
        # Update video status to completed
        self.db_client.update_video_status(video_id, "processed")
        
        print(f"Processing complete! Wiki page: {wiki_page.get('node', {}).get('title')}")
        
        return {
            "video_id": video_id,
            "wiki_id": wiki_id,
            "feishu_wiki_url": wiki_page.get('node', {}).get('url'),
            "frames_processed": len(frames),
            "status": "completed"
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process video and generate analysis documentation")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--user-id", required=True, help="User ID (UUID)")
    parser.add_argument("--space-id", required=True, help="Feishu Wiki space ID")
    
    args = parser.parse_args()
    
    analyzer = VideoAnalyzer()
    result = analyzer.process_video(args.video_path, args.user_id, args.space_id)
    print("\nResult:", result)