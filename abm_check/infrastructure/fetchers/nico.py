"""Nicovideo (Nico Nico Douga) fetcher implementation using RSS."""
import feedparser
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import yt_dlp

from abm_check.domain.models import Program, Episode, VideoFormat
from abm_check.domain.exceptions import FetchError, YtdlpError
from abm_check.infrastructure.fetcher import BaseFetcher


class NicoFetcher(BaseFetcher):
    """Fetch Nicovideo channel information using RSS + yt-dlp."""

    def fetch_program_info(self, program_id: str) -> Program:
        """
        Fetch program information from Nicovideo channel.
        
        Args:
            program_id: Nicovideo channel name (e.g. "danime")
            
        Returns:
            Program object
        """
        # Try cache first
        cached_info = self._load_cache(program_id)
        if cached_info:
            all_episodes = []
            if 'entries' in cached_info and cached_info['entries']:
                for entry in cached_info['entries']:
                    if entry:
                        all_episodes.append(self._convert_to_episode(entry))
            return self._convert_to_program_with_entries(cached_info, all_episodes, program_id)

        # Fetch RSS feed
        rss_url = f"https://ch.nicovideo.jp/{program_id}/video?rss=2.0"
        
        try:
            feed = feedparser.parse(rss_url)
            
            if feed.bozo and not feed.entries:
                raise FetchError(program_id, f"Failed to parse RSS feed: {feed.get('bozo_exception', 'Unknown error')}")
            
            # Extract video IDs from RSS entries
            video_ids = []
            for entry in feed.entries:
                # Extract video ID from link (e.g., https://www.nicovideo.jp/watch/so12345)
                link = entry.get('link', '')
                match = re.search(r'/watch/(so\d+|sm\d+)', link)
                if match:
                    video_ids.append(match.group(1))
            
            if not video_ids:
                raise FetchError(program_id, "No video IDs found in RSS feed")
            
            # Fetch details for each video using yt-dlp
            episodes = []
            ydl_opts = self.config.ytdlp_opts
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for video_id in video_ids[:50]:  # Limit to 50 most recent
                    try:
                        video_url = f"https://www.nicovideo.jp/watch/{video_id}"
                        info = ydl.extract_info(video_url, download=False)
                        if info:
                            episodes.append(self._convert_to_episode(info))
                    except Exception as e:
                        # Log but continue if individual video fails
                        print(f"Warning: Failed to fetch {video_id}: {e}")
                        continue
            
            # Create synthetic info dict for caching
            synthetic_info = {
                'id': program_id,
                'title': feed.feed.get('title', program_id),
                'description': feed.feed.get('description', ''),
                'webpage_url': f"https://ch.nicovideo.jp/{program_id}",
                'thumbnail': '',
                'entries': [ep.__dict__ for ep in episodes]
            }
            
            self._save_cache(program_id, synthetic_info)
            return self._convert_to_program_with_entries(synthetic_info, episodes, program_id)
            
        except FetchError:
            raise
        except Exception as e:
            raise FetchError(program_id, str(e))

    def _convert_to_program_with_entries(self, info: Dict[str, Any], episodes: list, program_id: str) -> Program:
        """Convert info dict and episode list to Program model."""
        now = datetime.now()
        
        # Find max episode number
        latest_ep_number = 0
        if episodes:
            numbered_eps = [ep.number for ep in episodes if ep.number > 0]
            if numbered_eps:
                latest_ep_number = max(numbered_eps)
        
        return Program(
            id=program_id,
            title=info.get('title', program_id),
            description=info.get('description', ''),
            url=info.get('webpage_url', f"https://ch.nicovideo.jp/{program_id}"),
            thumbnail_url=info.get('thumbnail', ''),
            total_episodes=len(episodes),
            latest_episode_number=latest_ep_number,
            episodes=episodes,
            fetched_at=now,
            updated_at=now,
            platform='niconico'
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
        
        # Nicovideo: check availability
        availability = entry.get('availability', '')
        is_premium = availability == 'premium_only'
        is_downloadable = has_formats and not is_premium
        
        # Episode number from yt-dlp or title parsing
        episode_number = entry.get('episode_number', 0)
        
        return Episode(
            id=entry.get('id', ''),
            number=episode_number,
            title=entry.get('title', ''),
            description=entry.get('description', ''),
            duration=int(entry.get('duration', 0)),
            thumbnail_url=entry.get('thumbnail', ''),
            is_downloadable=is_downloadable,
            is_premium_only=is_premium,
            download_url=entry.get('webpage_url') if is_downloadable else None,
            formats=formats,
            upload_date=entry.get('upload_date'),
            expiration_date=None
        )
