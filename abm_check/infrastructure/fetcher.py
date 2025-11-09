"""ABEMA program information fetcher using yt-dlp."""
import yt_dlp
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from abm_check.domain.models import Program, Episode, VideoFormat
from abm_check.domain.exceptions import FetchError, SeasonDetectionError, YtdlpError
from abm_check.config import get_config


class AbemaFetcher:
    """Fetch ABEMA program information using yt-dlp."""
    
    def __init__(self, config=None):
        """Initialize fetcher with configuration."""
        self.config = config or get_config()
        self.cache_dir = Path(self.config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, program_id: str) -> Path:
        """Get the path for a program's cache file."""
        return self.cache_dir / f"{program_id}.json"

    def _load_cache(self, program_id: str) -> Optional[Dict[str, Any]]:
        """Load program info from cache if valid."""
        cache_file = self._get_cache_path(program_id)
        if not cache_file.exists():
            return None
        
        # Check cache age
        file_mtime = cache_file.stat().st_mtime
        if (time.time() - file_mtime) > self.config.cache_ttl:
            return None # Cache expired
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Corrupted cache file, delete it
            cache_file.unlink(missing_ok=True)
            return None

    def _save_cache(self, program_id: str, info: Dict[str, Any]) -> None:
        """Save program info to cache."""
        cache_file = self._get_cache_path(program_id)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
        except Exception:
            # If saving fails, delete the partial/corrupted file
            cache_file.unlink(missing_ok=True)

    def fetch_program_info(self, program_id: str) -> Program:
        """
        Fetch program information from ABEMA.
        
        Args:
            program_id: Program ID (e.g., "26-249")
            
        Returns:
            Program object with all information
            
        Raises:
            FetchError: If fetching fails
        """
        # Try to load from cache first
        cached_info = self._load_cache(program_id)
        if cached_info:
            # If cache hit, convert and return
            all_episodes = []
            if 'entries' in cached_info and cached_info['entries']:
                for entry in cached_info['entries']:
                    if entry:
                        all_episodes.append(self._convert_to_episode(entry))
            return self._convert_to_program_with_episodes(cached_info, all_episodes)

        # If not in cache, fetch from network
        url = f"{self.config.base_url}/{program_id}"
        
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
                
                first_season_count = len(all_episodes)
                
                if first_season_count >= self.config.season_threshold:
                    season = 2
                    while season <= self.config.max_seasons:
                        season_url = self.config.season_url_pattern.format(
                            program_id=program_id,
                            season=season
                        )
                        try:
                            season_info = ydl.extract_info(season_url, download=False)
                            
                            if 'entries' in season_info and season_info['entries']:
                                season_episodes = []
                                for entry in season_info['entries']:
                                    if entry:
                                        season_episodes.append(self._convert_to_episode(entry))
                                
                                if season_episodes:
                                    all_episodes.extend(season_episodes)
                                    season += 1
                                else:
                                    break
                            else:
                                break
                        except yt_dlp.utils.DownloadError as e:
                            # Season not found, which is an expected outcome.
                            break
                
                # Save to cache before returning
                self._save_cache(program_id, info)
                return self._convert_to_program_with_episodes(info, all_episodes)
                
        except YtdlpError:
            raise
        except FetchError: # Re-raise FetchError from inside
            raise
        except Exception as e:
            raise FetchError(program_id, str(e))
    
    def _convert_to_program_with_episodes(self, info: Dict[str, Any], episodes: list) -> Program:
        """Convert yt-dlp info dict and episode list to Program model."""
        now = datetime.now()
        
        latest_ep_number = 0
        if episodes:
            regular_episodes = [ep.number for ep in episodes if ep.number and ep.number < 100]
            if regular_episodes:
                latest_ep_number = max(regular_episodes)
        
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
            updated_at=now
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
        
        availability = entry.get('availability', '')
        is_premium = availability == 'premium_only'
        is_downloadable = has_formats and not is_premium
        
        return Episode(
            id=entry.get('id', ''),
            number=entry.get('episode_number', 0),
            title=entry.get('title', ''),
            description=entry.get('description', ''),
            duration=int(entry.get('duration', 0)),
            thumbnail_url=entry.get('thumbnail', ''),
            is_downloadable=is_downloadable,
            is_premium_only=is_premium,
            download_url=entry.get('url') if is_downloadable else None,
            formats=formats,
            upload_date=entry.get('upload_date')
        )
