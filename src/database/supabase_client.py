"""
Supabase database client
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
import pytz

from src.config import SUPABASE_URL, SUPABASE_KEY, TIMEZONE
from src.utils.logger import get_logger

class SupabaseClient:
    """Supabase database client for managing posts"""

    def __init__(self):
        self.logger = get_logger('supabase')

        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.tz = pytz.timezone(TIMEZONE)
        self.logger.info("Supabase client initialized successfully")

    def _clean_content(self, content: str) -> str:
        """Clean content to avoid JSON serialization issues"""
        if not content:
            return ""

        # Remove null bytes and other problematic characters
        content = content.replace('\x00', '')

        # Ensure valid UTF-8
        content = content.encode('utf-8', errors='ignore').decode('utf-8')

        return content.strip()

    def create_daily_post(
        self,
        title: str,
        content: str,
        date: datetime,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create or update daily blog post

        Args:
            title: Post title
            content: Post content (Markdown format)
            date: Post date
            description: Post description/summary
            tags: Post tags

        Returns:
            Created/updated post data
        """
        try:
            # Generate slug (format: blockchain-daily-2025-11-23)
            date_str = date.strftime('%Y-%m-%d')
            slug = f"blockchain-daily-{date_str}"

            # Clean content to avoid JSON issues
            cleaned_content = self._clean_content(content)
            cleaned_description = self._clean_content(description or f"区块链每日观察 - {date_str}")
            cleaned_title = self._clean_content(title)

            # Log cleaned content length
            self.logger.info(f"Original content length: {len(content)}, Cleaned: {len(cleaned_content)}")

            # Prepare data
            post_data = {
                'slug': slug,
                'title': cleaned_title,
                'date': date_str,
                'content': cleaned_content,
                'description': cleaned_description,
                'tags': tags or ['区块链', '每日观察']
            }

            # Check if exists
            existing = self.get_post_by_slug(slug)

            if existing:
                self.logger.info(f"Post with slug '{slug}' already exists, updating...")
                result = self.client.table('posts').update(post_data).eq('slug', slug).execute()
            else:
                self.logger.info(f"Creating new post with slug '{slug}'...")
                result = self.client.table('posts').insert(post_data).execute()

            if result.data:
                self.logger.info(f"Successfully saved post: {slug}")
                return result.data[0]
            else:
                raise Exception("No data returned from Supabase")

        except Exception as e:
            self.logger.error(f"Error creating/updating post: {e}")
            self.logger.error(f"Post data keys: {list(post_data.keys()) if 'post_data' in locals() else 'N/A'}")
            raise

    def get_post_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get post by slug"""
        try:
            result = self.client.table('posts').select('*').eq('slug', slug).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            # Don't treat "not found" as an error
            if 'PGRST' not in str(e):
                self.logger.warning(f"Error checking post by slug '{slug}': {e}")
            return None

    def get_post_by_date(self, date: datetime) -> Optional[Dict[str, Any]]:
        """Get post by date"""
        date_str = date.strftime('%Y-%m-%d')
        try:
            result = self.client.table('posts').select('*').eq('date', date_str).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error fetching post by date '{date_str}': {e}")
            return None

    def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts"""
        try:
            result = self.client.table('posts').select('*').order('date', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            self.logger.error(f"Error fetching recent posts: {e}")
            return []

    def delete_post(self, slug: str) -> bool:
        """Delete post"""
        try:
            result = self.client.table('posts').delete().eq('slug', slug).execute()
            self.logger.info(f"Post '{slug}' deleted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting post '{slug}': {e}")
            return False
