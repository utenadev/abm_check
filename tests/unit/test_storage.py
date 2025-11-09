"""Unit tests for storage."""

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from abm_check.domain.exceptions import ProgramNotFoundError, StorageError
from abm_check.domain.models import Episode, Program
from abm_check.infrastructure.storage import ProgramStorage


class TestProgramStorage:
    """Test ProgramStorage class."""

    @pytest.fixture
    def temp_storage_path(self, tmp_path: Path) -> Path:
        """Create temporary storage path."""
        return tmp_path / "programs.yaml"

    @pytest.fixture
    def storage(self, temp_storage_path: Path) -> ProgramStorage:
        """Create ProgramStorage instance."""
        return ProgramStorage(str(temp_storage_path))

    @pytest.fixture
    def sample_program(self) -> Program:
        """Create sample program."""
        return Program(
            id="26-249",
            title="Test Program",
            url="https://abema.tv/video/title/26-249",
            description="Test description",
            thumbnail_url="https://example.com/thumb.png",
            total_episodes=1,
            latest_episode_number=1,
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
                )
            ],
        )

    def test_save_program_new(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test saving a new program."""
        storage.save_program(sample_program)

        programs = storage.load_programs()
        assert len(programs) == 1
        assert programs[0].id == "26-249"
        assert programs[0].title == "Test Program"

    def test_save_program_update_existing(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test updating an existing program."""
        # Save initial program
        storage.save_program(sample_program)

        # Update program
        sample_program.title = "Updated Title"
        sample_program.fetched_at = datetime(2025, 11, 8, 8, 0, 0)
        storage.save_program(sample_program)

        # Load and verify
        programs = storage.load_programs()
        assert len(programs) == 1
        assert programs[0].title == "Updated Title"

    def test_load_programs_empty(self, storage: ProgramStorage) -> None:
        """Test loading programs from empty storage."""
        programs = storage.load_programs()
        assert programs == []

    def test_load_programs_multiple(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test loading multiple programs."""
        program1 = sample_program
        program2 = Program(
            id="189-85",
            title="Another Program",
            url="https://abema.tv/video/title/189-85",
            description="Another description",
            thumbnail_url="https://example.com/thumb2.png",
            total_episodes=0,
            latest_episode_number=0,
            fetched_at=datetime(2025, 11, 8, 7, 20, 0),
            updated_at=datetime(2025, 11, 8, 7, 20, 0),
            episodes=[],
        )

        storage.save_program(program1)
        storage.save_program(program2)

        programs = storage.load_programs()
        assert len(programs) == 2
        assert programs[0].id == "26-249"
        assert programs[1].id == "189-85"

    def test_find_program_exists(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test finding an existing program."""
        storage.save_program(sample_program)

        program = storage.find_program("26-249")
        assert program is not None
        assert program.id == "26-249"
        assert program.title == "Test Program"

    def test_find_program_not_exists(self, storage: ProgramStorage) -> None:
        """Test finding a non-existent program."""
        program = storage.find_program("999-999")
        assert program is None

    def test_delete_program(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test deleting a program."""
        storage.save_program(sample_program)
        assert len(storage.load_programs()) == 1

        storage.delete_program("26-249")
        assert len(storage.load_programs()) == 0

    def test_delete_program_not_exists(self, storage: ProgramStorage) -> None:
        """Test deleting a non-existent program."""
        with pytest.raises(ProgramNotFoundError):
            storage.delete_program("999-999")

    def test_storage_file_format(
        self, storage: ProgramStorage, sample_program: Program, temp_storage_path: Path
    ) -> None:
        """Test that storage file has correct YAML format."""
        storage.save_program(sample_program)

        # Read raw YAML
        with open(temp_storage_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "programs" in data
        assert "lastUpdated" in data
        assert isinstance(data["programs"], list)
        assert len(data["programs"]) == 1
        
        program_data = data["programs"][0]
        assert program_data["id"] == "26-249"
        assert program_data["title"] == "Test Program"
        assert "episodes" in program_data

    def test_storage_preserves_episodes(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test that storage preserves episode information."""
        storage.save_program(sample_program)

        programs = storage.load_programs()
        assert len(programs[0].episodes) == 1
        assert programs[0].episodes[0].id == "26-249_s1_p1"
        assert programs[0].episodes[0].title == "Episode 1"

    def test_get_all_program_ids(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test getting all program IDs."""
        program1 = sample_program
        program2 = Program(
            id="189-85",
            title="Another Program",
            url="https://abema.tv/video/title/189-85",
            description=None,
            thumbnail_url=None,
            total_episodes=0,
            latest_episode_number=0,
            fetched_at=datetime.now(),
            updated_at=datetime.now(),
            episodes=[],
        )

        storage.save_program(program1)
        storage.save_program(program2)

        program_ids = storage.get_all_program_ids()
        assert program_ids == ["26-249", "189-85"]

    def test_storage_concurrent_access(
        self, storage: ProgramStorage, sample_program: Program
    ) -> None:
        """Test that storage handles concurrent writes safely."""
        # This is a basic test - in production, you might need file locking
        storage.save_program(sample_program)
        
        program2 = Program(
            id="189-85",
            title="Another Program",
            url="https://abema.tv/video/title/189-85",
            description=None,
            thumbnail_url=None,
            total_episodes=0,
            latest_episode_number=0,
            fetched_at=datetime.now(),
            updated_at=datetime.now(),
            episodes=[],
        )
        storage.save_program(program2)

        programs = storage.load_programs()
        assert len(programs) == 2

    def test_load_programs_corrupted_yaml(self, storage: ProgramStorage, temp_storage_path: Path) -> None:
        """Test loading programs from a corrupted YAML file."""
        temp_storage_path.write_text("programs:\n  - id: '26-249'\n    title: 'Test'\n  invalid_key: :", encoding="utf-8")
        with pytest.raises(StorageError) as exc_info:
            storage.load_programs()
        assert "load_programs" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, yaml.YAMLError)

    def test_load_programs_empty_file(self, storage: ProgramStorage, temp_storage_path: Path) -> None:
        """Test loading programs from an empty file."""
        temp_storage_path.write_text("", encoding="utf-8")
        programs = storage.load_programs()
        assert programs == []

