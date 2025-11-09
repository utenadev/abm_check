"""Domain models for abm_check."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class VideoFormat:
    """Video format information."""
    
    format_id: str
    resolution: str
    tbr: float
    url: str


@dataclass
class Episode:
    """Episode information."""
    
    id: str
    number: int
    title: str
    description: str
    duration: int
    thumbnail_url: str
    is_downloadable: bool
    is_premium_only: bool
    download_url: Optional[str]
    formats: List[VideoFormat]
    upload_date: Optional[str]
    
    def get_episode_url(self, program_id: str = None) -> str:
        """
        Generate episode URL from episode ID.
        
        Args:
            program_id: Program ID (kept for backward compatibility, not used)
            
        Returns:
            Episode URL
        """
        from abm_check.config import get_config
        config = get_config()
        return f"{config.episode_base_url}/{self.id}"


@dataclass
class Program:
    """Program information."""
    
    id: str
    title: str
    description: str
    url: str
    thumbnail_url: str
    total_episodes: int
    latest_episode_number: int
    episodes: List[Episode]
    fetched_at: datetime
    updated_at: datetime
