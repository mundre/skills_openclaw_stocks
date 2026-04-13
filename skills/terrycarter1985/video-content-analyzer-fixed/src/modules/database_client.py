# Supabase database module
import os
import logging
from typing import Dict, List, Optional
from supabase import create_client, Client
from dataclasses import asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self, url: str = None, service_key: str = None):
        self.supabase_url = url or os.getenv("SUPABASE_URL")
        self.service_key = service_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.service_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables must be set")
        
        self.client: Client = create_client(self.supabase_url, self.service_key)
    
    def save_video_asset(self, user_id: str, filename: str, storage_path: str, duration: float, file_size: int) -> str:
        """Save video asset record to database"""
        data = {
            "user_id": user_id,
            "original_filename": filename,
            "storage_path": storage_path,
            "duration_seconds": float(duration) if duration is not None else None,
            "file_size_bytes": int(file_size) if file_size is not None else None,
            "status": "processing"
        }
        
        try:
            # Ensure user exists in profiles table (create if not - for service role operations)
            profiles = self.client.table("profiles").select("id").eq("id", user_id).execute()
            if not profiles.data:
                logger.info(f"User {user_id} not found in profiles, creating...")
                self.client.table("profiles").insert({
                    "id": user_id,
                    "username": f"user_{user_id[:8]}",
                    "full_name": "System User"
                }).execute()
            
            response = self.client.table("video_assets").insert(data).execute()
            return response.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to save video asset: {str(e)}")
            raise RuntimeError(f"Database error saving video: {str(e)}") from e
    
    def update_video_status(self, video_id: str, status: str) -> None:
        """Update video processing status"""
        try:
            self.client.table("video_assets").update({"status": status}).eq("id", video_id).execute()
        except Exception as e:
            logger.error(f"Failed to update video status: {str(e)}")
    
    def save_frame(self, video_id: str, frame_number: int, timestamp: float, storage_path: str, width: int, height: int, ocr_text: str = None, content_tags: List[str] = None) -> str:
        """Save extracted frame record to database"""
        data = {
            "video_id": video_id,
            "frame_number": int(frame_number) if frame_number is not None else 0,
            "timestamp_seconds": float(timestamp) if timestamp is not None else 0.0,
            "storage_path": storage_path,
            "width": int(width) if width is not None else None,
            "height": int(height) if height is not None else None,
            "ocr_text": ocr_text,
            "content_tags": content_tags or []
        }
        
        try:
            response = self.client.table("video_frames").insert(data).execute()
            return response.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to save frame: {str(e)}")
            raise RuntimeError(f"Database error saving frame: {str(e)}") from e
    
    def save_search_results(self, frame_id: str, query: str, results: List) -> None:
        """Save search results for a frame"""
        records = []
        for result in results:
            records.append({
                "frame_id": frame_id,
                "query": query,
                "search_engine": "google_custom_search",
                "result_url": result.url,
                "title": result.title,
                "snippet": result.snippet,
                "relevance_score": float(result.relevance_score) if result.relevance_score is not None else 0.0
            })
        
        if records:
            try:
                self.client.table("search_results").insert(records).execute()
            except Exception as e:
                logger.error(f"Failed to save search results: {str(e)}")
    
    def save_wiki_page(self, user_id: str, title: str, content: str, video_id: str, frame_ids: List[str]) -> str:
        """Save generated wiki page record"""
        data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "source_video_id": video_id,
            "source_frame_ids": frame_ids
        }
        
        try:
            response = self.client.table("wiki_pages").insert(data).execute()
            return response.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to save wiki page: {str(e)}")
            raise RuntimeError(f"Database error saving wiki page: {str(e)}") from e