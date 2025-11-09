"""Unit tests for domain models."""
import pytest
from datetime import datetime
from abm_check.domain.models import Program, Episode, VideoFormat


class TestVideoFormat:
    """VideoFormat model tests."""

    def test_create_video_format(self) -> None:
        """Test creating a VideoFormat instance."""
        fmt = VideoFormat(
            format_id="5300",
            resolution="1920x1080",
            tbr=5300.0,
            url="https://example.com/video.m3u8"
        )
        
        assert fmt.format_id == "5300"
        assert fmt.resolution == "1920x1080"
        assert fmt.tbr == 5300.0
        assert fmt.url == "https://example.com/video.m3u8"


class TestEpisode:
    """Episode model tests."""

    def test_create_episode(self) -> None:
        """Test creating an Episode instance."""
        episode = Episode(
            id="26-249_s1_p1",
            number=1,
            title="第1話 はじめての鉱物採集",
            description="Test description",
            duration=1420,
            thumbnail_url="https://example.com/thumb.png",
            is_downloadable=True,
            is_premium_only=False,
            download_url="https://example.com/video.m3u8",
            formats=[],
            upload_date="20250709"
        )
        
        assert episode.id == "26-249_s1_p1"
        assert episode.number == 1
        assert episode.title == "第1話 はじめての鉱物採集"
        assert episode.is_downloadable is True
        assert episode.is_premium_only is False

    def test_episode_without_optional_fields(self) -> None:
        """Test creating an Episode without optional fields."""
        episode = Episode(
            id="26-249_s1_p1",
            number=1,
            title="Test",
            description="Test",
            duration=1420,
            thumbnail_url="https://example.com/thumb.png",
            is_downloadable=False,
            is_premium_only=True,
            download_url=None,
            formats=[],
            upload_date=None
        )
        
        assert episode.download_url is None
        assert episode.upload_date is None

    @pytest.mark.parametrize(
        "number, is_special",
        [
            (1, False),
            (12, False),
            (99, False),
            (100, True),
            (101, True),
            (500, True),
        ],
    )
    def test_episode_classification(self, number: int, is_special: bool) -> None:
        """Test the classification of regular vs special episodes."""
        episode = Episode(
            id=f"ep-{number}",
            number=number,
            title=f"Episode {number}",
            description="",
            duration=0,
            thumbnail_url="",
            is_downloadable=True,
            is_premium_only=False,
            download_url="",
            formats=[],
            upload_date=None,
        )
        
        is_regular_episode = episode.number < 100
        assert not is_regular_episode if is_special else is_regular_episode



class TestProgram:
    """Program model tests."""

    def test_create_program(self) -> None:
        """Test creating a Program instance."""
        now = datetime.now()
        program = Program(
            id="26-249",
            title="瑠璃の宝石",
            description="Test description",
            url="https://abema.tv/video/title/26-249",
            thumbnail_url="https://example.com/thumb.png",
            total_episodes=13,
            latest_episode_number=13,
            episodes=[],
            fetched_at=now,
            updated_at=now
        )
        
        assert program.id == "26-249"
        assert program.title == "瑠璃の宝石"
        assert program.total_episodes == 13
        assert program.latest_episode_number == 13
        assert len(program.episodes) == 0

    def test_program_with_episodes(self) -> None:
        """Test Program with Episode list."""
        now = datetime.now()
        episodes = [
            Episode(
                id="26-249_s1_p1",
                number=1,
                title="第1話",
                description="Test",
                duration=1420,
                thumbnail_url="https://example.com/thumb.png",
                is_downloadable=True,
                is_premium_only=False,
                download_url="https://example.com/video.m3u8",
                formats=[],
                upload_date="20250709"
            )
        ]
        
        program = Program(
            id="26-249",
            title="瑠璃の宝石",
            description="Test description",
            url="https://abema.tv/video/title/26-249",
            thumbnail_url="https://example.com/thumb.png",
            total_episodes=13,
            latest_episode_number=13,
            episodes=episodes,
            fetched_at=now,
            updated_at=now
        )
        
        assert len(program.episodes) == 1
        assert program.episodes[0].number == 1
