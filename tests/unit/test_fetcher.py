"""Unit tests for program fetcher."""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from abm_check.domain.exceptions import FetchError, YtdlpError
from abm_check.domain.models import Episode, Program
from abm_check.infrastructure.fetcher import AbemaFetcher


class TestAbemaFetcher:
    """Test AbemaFetcher class."""

    @pytest.fixture
    def mock_program_info(self) -> dict[str, Any]:
        """Mock program info from yt-dlp."""
        return {
            "id": "26-249",
            "title": "瑠璃の宝石",
            "webpage_url": "https://abema.tv/video/title/26-249",
            "description": "瑠璃の宝石等、今期アニメ(最新作)の見逃し配信",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [
                {
                    "id": "26-249_s1_p1",
                    "title": "第1話 はじめての鉱物採集",
                    "url": "https://abema.tv/video/episode/26-249_s1_p1",
                    "duration": 1440,
                    "season_number": 1,
                    "episode_number": 1,
                    "thumbnail": "https://example.com/ep1.jpg",
                },
                {
                    "id": "26-249_s1_p2",
                    "title": "第2話 金色の価値",
                    "url": "https://abema.tv/video/episode/26-249_s1_p2",
                    "duration": 1440,
                    "season_number": 1,
                    "episode_number": 2,
                    "thumbnail": "https://example.com/ep2.jpg",
                },
            ],
        }

    @pytest.fixture
    def fetcher(self, tmp_path: Path) -> AbemaFetcher:
        """Create AbemaFetcher instance with a temporary cache directory."""
        from abm_check.config import Config
        config = Config()
        config.config['cache']['cache_dir'] = str(tmp_path / "cache")
        config.config['cache']['cache_ttl'] = 0 # Disable cache for most tests
        return AbemaFetcher(config=config)

    @pytest.fixture
    def mock_ydl_extract_info(self) -> MagicMock:
        """Mock yt_dlp.YoutubeDL.extract_info."""
        with patch("abm_check.infrastructure.fetcher.yt_dlp.YoutubeDL") as mock_ydl:
            yield mock_ydl.return_value.__enter__.return_value.extract_info

    def test_fetch_program_info(
        self, fetcher: AbemaFetcher, mock_program_info: dict[str, Any], mock_ydl_extract_info: MagicMock
    ) -> None:
        """Test fetching program information successfully."""
        mock_ydl_extract_info.return_value = mock_program_info

        program = fetcher.fetch_program_info("26-249")

        assert isinstance(program, Program)
        assert program.id == "26-249"
        assert program.title == "瑠璃の宝石"
        assert program.url == "https://abema.tv/video/title/26-249"
        assert program.description == "瑠璃の宝石等、今期アニメ(最新作)の見逃し配信"
        assert program.thumbnail_url == "https://example.com/thumb.png"
        assert len(program.episodes) == 2
        assert isinstance(program.fetched_at, datetime)
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_episodes(
        self, fetcher: AbemaFetcher, mock_program_info: dict[str, Any], mock_ydl_extract_info: MagicMock
    ) -> None:
        """Test fetching program episodes."""
        mock_ydl_extract_info.return_value = mock_program_info

        program = fetcher.fetch_program_info("26-249")

        assert len(program.episodes) == 2
        
        ep1 = program.episodes[0]
        assert isinstance(ep1, Episode)
        assert ep1.id == "26-249_s1_p1"
        assert ep1.title == "第1話 はじめての鉱物採集"
        assert ep1.duration == 1440
        assert ep1.number == 1

        ep2 = program.episodes[1]
        assert ep2.id == "26-249_s1_p2"
        assert ep2.title == "第2話 金色の価値"
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_no_episodes(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test fetching program with no episodes."""
        mock_info = {
            "id": "26-249",
            "title": "Test Program",
            "webpage_url": "https://abema.tv/video/title/26-249",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [],
        }

        mock_ydl_extract_info.return_value = mock_info

        program = fetcher.fetch_program_info("26-249")
        assert program.episodes == []
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_error(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test handling fetch errors."""
        mock_ydl_extract_info.side_effect = Exception("Network error")

        with pytest.raises(YtdlpError) as exc_info:
            fetcher.fetch_program_info("26-249")

        assert "Failed to extract info" in str(exc_info.value)
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_multi_season_program(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test fetching program with multiple seasons (>= 12 episodes triggers season detection)."""
        first_season_info = {
            "id": "26-249",
            "title": "Test Anime",
            "webpage_url": "https://abema.tv/video/title/26-249",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [
                {
                    "id": f"26-249_s1_p{i}",
                    "title": f"Episode {i}",
                    "duration": 1440,
                    "episode_number": i,
                    "thumbnail": "https://example.com/thumb.png",
                    "formats": [],
                }
                for i in range(1, 13)
            ],
        }
        
        second_season_info = {
            "id": "26-249",
            "title": "Test Anime",
            "webpage_url": "https://abema.tv/video/title/26-249?s=26-249_s2",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [
                {
                    "id": f"26-249_s2_p{i}",
                    "title": f"Season 2 Episode {i}",
                    "duration": 1440,
                    "episode_number": i,
                    "thumbnail": "https://example.com/thumb.png",
                    "formats": [],
                }
                for i in range(1, 6)
            ],
        }
        
        empty_season_info = {
            "id": "26-249",
            "title": "Test Anime",
            "webpage_url": "https://abema.tv/video/title/26-249?s=26-249_s3",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [],
        }
        
        mock_ydl_extract_info.side_effect = [
            first_season_info,
            second_season_info,
            empty_season_info,
        ]
        
        program = fetcher.fetch_program_info("26-249")
        
        assert len(program.episodes) == 17
        assert program.total_episodes == 17
        assert mock_ydl_extract_info.call_count == 3

    def test_fetch_program_with_premium_episodes(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test fetching program with premium-only episodes."""
        mock_info = {
            "id": "26-249",
            "title": "Test Program",
            "webpage_url": "https://abema.tv/video/title/26-249",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [
                {
                    "id": "26-249_s1_p1",
                    "title": "Episode 1 (Free)",
                    "duration": 1440,
                    "episode_number": 1,
                    "thumbnail": "https://example.com/ep1.jpg",
                    "availability": "public",
                    "formats": [{"format_id": "1", "resolution": "720p", "tbr": 1000, "url": "http://example.com"}],
                },
                {
                    "id": "26-249_s1_p2",
                    "title": "Episode 2 (Premium)",
                    "duration": 1440,
                    "episode_number": 2,
                    "thumbnail": "https://example.com/ep2.jpg",
                    "availability": "premium_only",
                    "formats": [],
                },
            ],
        }
        
        mock_ydl_extract_info.return_value = mock_info
        
        program = fetcher.fetch_program_info("26-249")
        
        assert len(program.episodes) == 2
        assert program.episodes[0].is_downloadable is True
        assert program.episodes[0].is_premium_only is False
        assert program.episodes[1].is_downloadable is False
        assert program.episodes[1].is_premium_only is True
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_with_special_episodes(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test fetching program with special episodes (episode number >= 100)."""
        mock_info = {
            "id": "26-249",
            "title": "Test Program",
            "webpage_url": "https://abema.tv/video/title/26-249",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [
                {
                    "id": "26-249_s1_p1",
                    "title": "Episode 1",
                    "duration": 1440,
                    "episode_number": 1,
                    "thumbnail": "https://example.com/ep1.jpg",
                },
                {
                    "id": "26-249_s1_p100",
                    "title": "PV",
                    "duration": 180,
                    "episode_number": 100,
                    "thumbnail": "https://example.com/pv.jpg",
                },
                {
                    "id": "26-249_s1_p101",
                    "title": "Special",
                    "duration": 300,
                    "episode_number": 101,
                    "thumbnail": "https://example.com/special.jpg",
                },
            ],
        }
        
        mock_ydl_extract_info.return_value = mock_info
        
        program = fetcher.fetch_program_info("26-249")
        
        assert len(program.episodes) == 3
        assert program.latest_episode_number == 1
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_info_returns_none(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test fetching program info when yt-dlp extract_info returns None."""
        mock_ydl_extract_info.return_value = None
        
        with pytest.raises(FetchError) as exc_info:
            fetcher.fetch_program_info("26-249")
        assert "yt-dlp returned no information" in str(exc_info.value)
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_info_no_entries_key(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test fetching program info when yt-dlp extract_info returns dict without 'entries' key."""
        mock_info = {
            "id": "26-249",
            "title": "Test Program",
            "webpage_url": "https://abema.tv/video/title/26-249",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            # No 'entries' key
        }
        mock_ydl_extract_info.return_value = mock_info
        
        program = fetcher.fetch_program_info("26-249")
        assert program.episodes == []
        assert program.total_episodes == 0
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_info_none_entry_in_entries(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test fetching program info when yt-dlp extract_info returns 'entries' with None entry."""
        mock_info = {
            "id": "26-249",
            "title": "Test Program",
            "webpage_url": "https://abema.tv/video/title/26-249",
            "description": "Test description",
            "thumbnail": "https://example.com/thumb.png",
            "entries": [
                {
                    "id": "26-249_s1_p1",
                    "title": "Episode 1",
                    "duration": 1440,
                    "episode_number": 1,
                    "thumbnail": "https://example.com/ep1.jpg",
                },
                None, # Invalid entry
                {
                    "id": "26-249_s1_p2",
                    "title": "Episode 2",
                    "duration": 1440,
                    "episode_number": 2,
                    "thumbnail": "https://example.com/ep2.jpg",
                },
            ],
        }
        mock_ydl_extract_info.return_value = mock_info
        
        program = fetcher.fetch_program_info("26-249")
        assert len(program.episodes) == 2
        assert program.episodes[0].id == "26-249_s1_p1"
        assert program.episodes[1].id == "26-249_s1_p2"
        mock_ydl_extract_info.assert_called_once()

    def test_fetch_program_info_cache_hit(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock, tmp_path: Path) -> None:
        """Test that fetch_program_info returns cached data if available and valid."""
        program_id = "cached-prog"
        cache_dir = tmp_path / "cache"
        cache_file = cache_dir / f"{program_id}.json"

        # Create a valid cache file
        cached_data = {
            "id": program_id,
            "title": "Cached Program",
            "webpage_url": "https://abema.tv/video/title/cached-prog",
            "entries": [
                {"id": "cached_ep1", "title": "Cached Episode 1", "episode_number": 1},
            ],
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f)
        
        # Ensure cache is considered valid (e.g., set TTL high or mtime recent)
        # For this test, we'll ensure the fetcher's config has a non-zero TTL
        fetcher.config.config['cache']['cache_ttl'] = 3600 # 1 hour

        program = fetcher.fetch_program_info(program_id)

        assert program.id == program_id
        assert program.title == "Cached Program"
        assert len(program.episodes) == 1
        assert program.episodes[0].id == "cached_ep1"
        mock_ydl_extract_info.assert_not_called() # Should not call yt-dlp

    def test_fetch_program_info_cache_miss_expired(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock, tmp_path: Path) -> None:
        """Test that fetch_program_info fetches from network if cache is expired."""
        program_id = "expired-prog"
        cache_dir = tmp_path / "cache"
        cache_file = cache_dir / f"{program_id}.json"

        # Create an expired cache file
        cached_data = {
            "id": program_id,
            "title": "Expired Program",
            "webpage_url": "https://abema.tv/video/title/expired-prog",
            "entries": [],
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f)
        
        # Set mtime to be old
        old_time = time.time() - fetcher.config.cache_ttl - 100
        os.utime(cache_file, (old_time, old_time))

        # Ensure cache is considered expired
        fetcher.config.config['cache']['cache_ttl'] = 1 # 1 second, so it expires quickly

        # Mock network response
        network_data = {
            "id": program_id,
            "title": "Network Program",
            "webpage_url": "https://abema.tv/video/title/network-prog",
            "entries": [
                {"id": "network_ep1", "title": "Network Episode 1", "episode_number": 1},
            ],
        }
        mock_ydl_extract_info.return_value = network_data

        program = fetcher.fetch_program_info(program_id)

        assert program.id == program_id
        assert program.title == "Network Program"
        assert len(program.episodes) == 1
        assert program.episodes[0].id == "network_ep1"
        mock_ydl_extract_info.assert_called_once() # Should call yt-dlp

    def test_fetch_program_info_cache_miss_no_file(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock) -> None:
        """Test that fetch_program_info fetches from network if no cache file exists."""
        program_id = "no-cache-file-prog"
        
        network_data = {
            "id": program_id,
            "title": "Network Program",
            "webpage_url": "https://abema.tv/video/title/network-prog",
            "entries": [
                {"id": "network_ep1", "title": "Network Episode 1", "episode_number": 1},
            ],
        }
        mock_ydl_extract_info.return_value = network_data

        program = fetcher.fetch_program_info(program_id)

        assert program.id == program_id
        assert program.title == "Network Program"
        assert len(program.episodes) == 1
        assert program.episodes[0].id == "network_ep1"
        mock_ydl_extract_info.assert_called_once() # Should call yt-dlp

    def test_fetch_program_info_cache_corrupted(self, fetcher: AbemaFetcher, mock_ydl_extract_info: MagicMock, tmp_path: Path) -> None:
        """Test that fetch_program_info fetches from network if cache file is corrupted."""
        program_id = "corrupted-cache-prog"
        cache_dir = tmp_path / "cache"
        cache_file = cache_dir / f"{program_id}.json"

        # Create a corrupted cache file
        cache_file.write_text("this is not valid json", encoding="utf-8")
        
        # Ensure cache is considered valid for this test
        fetcher.config.config['cache']['cache_ttl'] = 3600 # 1 hour
        
        network_data = {
            "id": program_id,
            "title": "Network Program",
            "webpage_url": "https://abema.tv/video/title/network-prog",
            "entries": [
                {"id": "network_ep1", "title": "Network Episode 1", "episode_number": 1},
            ],
        }
        mock_ydl_extract_info.return_value = network_data

        with patch('pathlib.Path.unlink') as mock_unlink:
            program = fetcher.fetch_program_info(program_id)

            assert program.id == program_id
            assert program.title == "Network Program"
            assert len(program.episodes) == 1
            assert program.episodes[0].id == "network_ep1"
            mock_ydl_extract_info.assert_called_once() # Should call yt-dlp
            mock_unlink.assert_called_once() # Corrupted cache should be deleted

