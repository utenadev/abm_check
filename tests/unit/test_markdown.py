"""Unit tests for markdown generator."""

from datetime import datetime
from pathlib import Path

import pytest

from abm_check.domain.models import Episode, Program
from abm_check.infrastructure.markdown import MarkdownGenerator


class TestMarkdownGenerator:
    """Test MarkdownGenerator class."""

    @pytest.fixture
    def temp_output_dir(self, tmp_path: Path) -> Path:
        """Create temporary output directory."""
        return tmp_path

    @pytest.fixture
    def generator(self, temp_output_dir: Path) -> MarkdownGenerator:
        """Create MarkdownGenerator instance."""
        return MarkdownGenerator()

    @pytest.fixture
    def sample_program(self) -> Program:
        """Create sample program."""
        return Program(
            id="26-249",
            title="Test Program",
            url="https://abema.tv/video/title/26-249",
            description="Test description",
            thumbnail_url="https://example.com/thumb.png",
            total_episodes=2,
            latest_episode_number=2,
            fetched_at=datetime(2025, 11, 8, 7, 16, 58),
            updated_at=datetime(2025, 11, 8, 7, 16, 58),
            episodes=[
                Episode(
                    id="26-249_s1_p1",
                    number=1,
                    title="Episode 1",
                    description="",
                    duration=1440,
                    thumbnail_url="https://example.com/ep1.jpg",
                    is_downloadable=True,
                    is_premium_only=False,
                    download_url=None,
                    formats=[],
                    upload_date=None,
                ),
                Episode(
                    id="26-249_s1_p2",
                    number=2,
                    title="Episode 2",
                    description="",
                    duration=1440,
                    thumbnail_url="https://example.com/ep2.jpg",
                    is_downloadable=True,
                    is_premium_only=False,
                    download_url=None,
                    formats=[],
                    upload_date=None,
                ),
            ],
        )

    def test_generate_program_md_content(
        self, generator: MarkdownGenerator, sample_program: Program
    ) -> None:
        """Test generating markdown content."""
        content = generator.generate_program_md(sample_program)

        assert "# Test Program" in content
        assert "26-249" in content
        assert "https://abema.tv/video/title/26-249" in content
        assert "Test description" in content
        assert "Episode 1" in content
        assert "Episode 2" in content

    def test_save_program_md(
        self,
        generator: MarkdownGenerator,
        sample_program: Program,
        temp_output_dir: Path,
    ) -> None:
        """Test saving markdown file."""
        file_path = generator.save_program_md(sample_program)

        assert Path(file_path).exists()
        assert Path(file_path).name == "program.md"

        # Check content
        content = Path(file_path).read_text(encoding="utf-8")
        assert "# Test Program" in content
        assert "Episode 1" in content

    def test_generate_md_with_no_episodes(
        self, generator: MarkdownGenerator
    ) -> None:
        """Test generating markdown for program with no episodes."""
        program = Program(
            id="test",
            title="Test",
            url="https://example.com",
            description=None,
            thumbnail_url=None,
            total_episodes=0,
            latest_episode_number=0,
            fetched_at=datetime.now(),
            updated_at=datetime.now(),
            episodes=[],
        )

        content = generator.generate_program_md(program)
        assert "# Test" in content
        assert "エピソード一覧" not in content

    def test_generate_md_with_long_description(
        self, generator: MarkdownGenerator
    ) -> None:
        """Test generating markdown with long description."""
        program = Program(
            id="test",
            title="Test",
            url="https://example.com",
            description="A" * 1000,  # Long description
            thumbnail_url=None,
            total_episodes=0,
            latest_episode_number=0,
            fetched_at=datetime.now(),
            updated_at=datetime.now(),
            episodes=[],
        )

        content = generator.generate_program_md(program)
        assert "# Test" in content
        assert "A" * 100 in content  # Should contain at least part of description
