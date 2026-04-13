# Feishu Wiki module - adapted from public source
import os
import requests
from typing import Dict, Optional

class FeishuWikiClient:
    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        self._access_token = None
        
        if not self.app_id or not self.app_secret:
            raise ValueError("FEISHU_APP_ID and FEISHU_APP_SECRET environment variables must be set")
    
    def _get_access_token(self) -> str:
        """Get valid access token"""
        if self._access_token:
            return self._access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            self._access_token = response.json()["tenant_access_token"]
            return self._access_token
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get Feishu access token: {str(e)}") from e
    
    def create_page(self, space_id: str, title: str, content: str, parent_node_token: str = None) -> Dict:
        """Create a new wiki page using document import API for proper markdown support"""
        # First create an empty wiki node
        url = "https://open.feishu.cn/open-apis/wiki/v2/nodes"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "space_id": space_id,
            "title": title,
            "node_type": "wiki"
        }
        
        if parent_node_token:
            payload["parent_node_token"] = parent_node_token
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            node_data = response.json()["data"]
            node_token = node_data["node"]["node_token"]
            obj_token = node_data["node"]["obj_token"]
            obj_type = node_data["node"]["obj_type"]
            
            # Now import markdown content using document import API
            import_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{obj_token}/markdown/import"
            import_payload = {
                "markdown": content,
                "timestamp": 0
            }
            
            import_response = requests.post(import_url, json=import_payload, headers=headers)
            if import_response.status_code != 200:
                print(f"Warning: Markdown import failed (falling back): {import_response.text}")
                # Fallback: Try the old content field method for older API versions
                update_url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes/{node_token}/content"
                requests.post(update_url, json={"content": content}, headers=headers)
            
            return node_data
        except requests.exceptions.RequestException as e:
            error_detail = e.response.text if e.response else str(e)
            raise RuntimeError(f"Failed to create wiki page: {error_detail}") from e
    
    def generate_page_content(self, video_name: str, frames_data: list) -> str:
        """Generate wiki page content from processed video frames
        Uses Feishu Wiki compatible Markdown format - fixes link rendering issue
        """
        content = f"# Video Analysis: {video_name}\n\n"
        content += "## Summary\n\n"
        content += f"Processed {len(frames_data)} frames from the video. Below are key findings:\n\n"
        
        for i, frame_data in enumerate(frames_data, 1):
            content += f"### Frame {i} (Time: {frame_data['timestamp']:.2f}s)\n\n"
            if frame_data.get('content_tags'):
                content += f"**Content Tags**: {', '.join(frame_data['content_tags'])}\n\n"
            
            if frame_data.get('search_results'):
                content += "**Related References**:\n"
                for j, result in enumerate(frame_data['search_results'][:3], 1):
                    title = result.get('title', 'No Title').replace('|', '-').replace(']', ')').replace('[', '(').strip()
                    url = result.get('url', '')
                    snippet = result.get('snippet', '').replace('\n', ' ').strip()
                    
                    # Feishu Wiki compatible link format
                    # Note: Feishu uses special markdown; URLs on their own line auto-link
                    content += f"{j}. **{title}**\n"
                    content += f"   🔗 Link: {url}\n"
                    if snippet:
                        content += f"   💡 {snippet[:200]}...\n"
                    content += "\n"
            
            content += "---\n\n"
        
        return content