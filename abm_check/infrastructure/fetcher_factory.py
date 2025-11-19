"""Factory for creating appropriate fetcher based on URL/ID."""
import re
from typing import Union
from abm_check.infrastructure.fetcher import BaseFetcher
from abm_check.infrastructure.fetchers.tver import TVerFetcher
from abm_check.infrastructure.fetchers.nico import NicoFetcher
from abm_check.config import get_config


class FetcherFactory:
    """Factory to create appropriate fetcher based on URL or ID."""
    
    def __init__(self, config=None):
        """Initialize factory with configuration."""
        self.config = config or get_config()
    
    def create_fetcher(self, url_or_id: str) -> tuple[BaseFetcher, str]:
        """
        Create appropriate fetcher based on URL or ID.
        
        Args:
            url_or_id: URL or ID string
            
        Returns:
            Tuple of (fetcher instance, program_id)
            
        Raises:
            ValueError: If URL/ID format is not recognized
        """
        # Import here to avoid circular dependency
        from abm_check.infrastructure.fetcher import AbemaFetcher
        
        url_or_id = url_or_id.strip()
        
        # TVer detection
        if 'tver.jp' in url_or_id:
            # Extract series ID from TVer URL
            # Format: https://tver.jp/series/sr12345
            match = re.search(r'/series/(sr\w+)', url_or_id)
            if match:
                series_id = match.group(1)
                return TVerFetcher(self.config), series_id
            # Also support direct series ID
            elif url_or_id.startswith('sr'):
                return TVerFetcher(self.config), url_or_id
            else:
                raise ValueError(f"Could not extract TVer series ID from: {url_or_id}")
        
        # Nicovideo detection
        elif 'nicovideo.jp' in url_or_id or 'ch.nicovideo.jp' in url_or_id:
            # Extract channel name from URL
            # Format: https://ch.nicovideo.jp/danime
            match = re.search(r'ch\.nicovideo\.jp/([^/\?]+)', url_or_id)
            if match:
                channel_name = match.group(1)
                return NicoFetcher(self.config), channel_name
            else:
                # Assume it's a channel name
                return NicoFetcher(self.config), url_or_id
        
        # AbemaTV detection (default)
        elif 'abema.tv' in url_or_id:
            # Extract program ID from AbemaTV URL
            # Format: https://abema.tv/video/title/26-156
            match = re.search(r'/title/([^/\?]+)', url_or_id)
            if match:
                program_id = match.group(1)
                return AbemaFetcher(self.config), program_id
            else:
                raise ValueError(f"Could not extract AbemaTV program ID from: {url_or_id}")
        
        # If no URL detected, treat as ID and guess platform
        else:
            # TVer series IDs start with 'sr'
            if url_or_id.startswith('sr'):
                return TVerFetcher(self.config), url_or_id
            # AbemaTV IDs typically have format like "26-156"
            elif re.match(r'^\d+-\d+$', url_or_id):
                return AbemaFetcher(self.config), url_or_id
            # Otherwise assume it's a Nicovideo channel name
            else:
                return NicoFetcher(self.config), url_or_id
