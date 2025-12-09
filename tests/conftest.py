"""Pytest configuration file for shared fixtures and helpers."""
import pytest
from datetime import datetime, timedelta
from abm_check.domain.models import Episode, Program, VideoFormat

@pytest.fixture
def create_video_format():
    """Fixture factory to create a dummy VideoFormat."""
    def _create_video_format(format_id="184"):
        return VideoFormat(
            format_id=format_id,
            resolution="320x180",
            tbr=184.0,
            url="http://example.com/video.m3u8"
        )
    return _create_video_format

@pytest.fixture
def create_episode(create_video_format):
    """Fixture factory to create a dummy Episode."""
    def _create_episode(
        id: str,
        number: int,
        is_downloadable: bool = True,
        is_premium_only: bool = False,
        title: str = None,
        duration: int = 1420,
        thumbnail_url: str = "http://example.com/thumb.png"
    ) -> Episode:
        return Episode(
            id=id,
            number=number,
            title=title or f"Episode {number}",
            description=f"Description for episode {number}",
            duration=duration,
            thumbnail_url=thumbnail_url,
            is_downloadable=is_downloadable,
            is_premium_only=is_premium_only,
            download_url="http://example.com/video.m3u8" if is_downloadable else None,
            formats=[create_video_format()] if is_downloadable else [],
            upload_date="20250101"
        )
    return _create_episode

@pytest.fixture
def create_program():
    """Fixture factory to create a dummy Program."""
    def _create_program(id: str, episodes: list[Episode], title: str = None, fetched_at: datetime = None) -> Program:
        now = datetime.now()
        fetch_time = fetched_at or now - timedelta(days=1)
        return Program(
            id=id,
            title=title or f"Program {id}",
            description="Test program description",
            url=f"https://abema.tv/video/title/{id}",
            thumbnail_url="http://example.com/program.png",
            total_episodes=len(episodes),
            latest_episode_number=max([ep.number for ep in episodes if ep.number < 100] or [0]),
            episodes=episodes,
            fetched_at=fetch_time,
            updated_at=fetch_time
        )
    return _create_program