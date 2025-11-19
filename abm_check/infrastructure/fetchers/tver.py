"""TVer fetcher implementation."""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import yt_dlp

from abm_check.domain.models import Program, Episode, VideoFormat
from abm_check.domain.exceptions import FetchError, YtdlpError
from abm_check.infrastructure.fetcher import BaseFetcher

class TVerFetcher(BaseFetcher):
    """Fetch TVer program information using yt-dlp."""

    def fetch_program_info(self, program_id: str) -> Program:
        """
        Fetch program information from TVer.
        
        Args:
            program_id: TVer Series ID (e.g. "sr12345")
            
        Returns:
            Program object
        """
        # Try to load from cache first
        cached_info = self._load_cache(program_id)
        if cached_info:
            all_episodes = []
            if 'entries' in cached_info and cached_info['entries']:
                for entry in cached_info['entries']:
                    if entry:
                        all_episodes.append(self._convert_to_episode(entry))
            return self._convert_to_program_with_episodes(cached_info, all_episodes)

        # TVer series URL
        url = f"https://tver.jp/series/{program_id}"
        
        ydl_opts = self.config.ytdlp_opts
        
        try:
            all_episodes = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception as e:
                    raise YtdlpError(f"Failed to extract info from {url}: {str(e)}")
                
                if info is None:
                    raise FetchError(program_id, "yt-dlp returned no information.")

                if 'entries' in info and info['entries']:
                    for entry in info['entries']:
                        if entry:
                            all_episodes.append(self._convert_to_episode(entry))
                
                # Save to cache
                self._save_cache(program_id, info)
                return self._convert_to_program_with_episodes(info, all_episodes)
                
        except YtdlpError:
            raise
        except Exception as e:
            raise FetchError(program_id, str(e))

    def _convert_to_program_with_episodes(self, info: Dict[str, Any], episodes: list) -> Program:
        """Convert yt-dlp info dict and episode list to Program model."""
        now = datetime.now()
        
        # TVer doesn't strictly have "latest episode number" in the same way as anime seasons,
        # but we can try to find the max number if available, or just count.
        latest_ep_number = 0
        if episodes:
            numbered_eps = [ep.number for ep in episodes if ep.number > 0]
            if numbered_eps:
                latest_ep_number = max(numbered_eps)
        
        return Program(
            id=info.get('id', ''),
            title=info.get('title', ''),
            description=info.get('description', ''),
            url=info.get('webpage_url', ''),
            thumbnail_url=info.get('thumbnail', ''),
            total_episodes=len(episodes),
            latest_episode_number=latest_ep_number,
            episodes=episodes,
            fetched_at=now,
            updated_at=now,
            platform='tver'
        )

    def _convert_to_episode(self, entry: Dict[str, Any]) -> Episode:
        """Convert yt-dlp entry dict to Episode model."""
        formats_list = entry.get('formats', [])
        has_formats = len(formats_list) > 0
        
        formats = []
        for fmt in formats_list:
            formats.append(VideoFormat(
                format_id=fmt.get('format_id', ''),
                resolution=fmt.get('resolution', ''),
                tbr=fmt.get('tbr', 0.0),
                url=fmt.get('url', '')
            ))
        
        # TVer specific: check availability
        # Usually TVer episodes are free if they are listed, but might be expired?
        # yt-dlp usually handles expiration by not returning formats or raising error.
        is_downloadable = has_formats
        
        # Try to extract expiration date
        # yt-dlp might put it in 'release_timestamp' (start) or custom fields.
        # Often TVer metadata in yt-dlp has 'timestamp' as upload date.
        # We might need to look for specific fields if yt-dlp supports them.
        # For now, we'll leave expiration_date None unless we find a reliable field.
        expiration_date = None
        
        # Attempt to parse episode number from title if 'episode_number' is missing
        episode_number = entry.get('episode_number', 0)
        
        return Episode(
            id=entry.get('id', ''),
            number=episode_number,
            title=entry.get('title', ''),
            description=entry.get('description', ''),
            duration=int(entry.get('duration', 0)),
            thumbnail_url=entry.get('thumbnail', ''),
            is_downloadable=is_downloadable,
            is_premium_only=False, # TVer is generally free (ad-supported)
            download_url=entry.get('webpage_url') if is_downloadable else None,
            formats=formats,
            upload_date=entry.get('upload_date'),
            expiration_date=expiration_date
        )
