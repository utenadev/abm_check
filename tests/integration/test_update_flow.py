"""Integration tests for the full update flow."""
import pytest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta

from abm_check.domain.models import Program, Episode, VideoFormat
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.infrastructure.updater import ProgramUpdater
from abm_check.infrastructure.download_list import DownloadListGenerator

@pytest.fixture
def temp_storage(tmp_path: Path) -> ProgramStorage:
    """Create a ProgramStorage instance using a temporary directory."""
    db_path = tmp_path / "programs.yaml"
    return ProgramStorage(data_file=str(db_path))

@patch('abm_check.infrastructure.fetcher.AbemaFetcher.fetch_program_info')
def test_full_update_flow(mock_fetch, temp_storage: ProgramStorage, tmp_path: Path, create_episode, create_program):
    """
    Test the full flow from updating a program to generating a download list.
    - Mocks only the fetcher to avoid network requests.
    - Uses real Storage, Updater, and DownloadListGenerator.
    """
    program_id = "integration-test-1"
    output_dir = tmp_path / "output"
    download_list_path = output_dir / "download_urls.txt"
    
    # --- 1. Initial state setup ---
    # Create an old version of the program and save it to storage.
    now = datetime.now()
    old_fetched_at = now - timedelta(days=2)
    
    old_ep1 = create_episode("ep1", 1, is_downloadable=False, is_premium_only=True)
    old_program = create_program(program_id, [old_ep1], fetched_at=old_fetched_at)
    
    temp_storage.save_program(old_program)
    
    # --- 2. Mock the new program data that the fetcher will return ---
    # The new version has a new episode and the old one is now free.
    new_ep1 = create_episode("ep1", 1, is_downloadable=True, is_premium_only=False)
    new_ep2 = create_episode("ep2", 2, is_downloadable=True)
    new_program = create_program(program_id, [new_ep1, new_ep2], fetched_at=old_fetched_at)
    mock_fetch.return_value = new_program

    # --- 3. Run the update process ---
    # Initialize components with the temporary storage
    updater = ProgramUpdater(storage=temp_storage)
    diff = updater.update_program(program_id)

    # --- 4. Assertions for the update process ---
    assert diff is not None
    assert len(diff.new_episodes) == 1
    assert diff.new_episodes[0].id == "ep2"
    assert len(diff.premium_to_free) == 1
    assert diff.premium_to_free[0].id == "ep1"

    # Check if the program was updated in storage
    updated_program_from_storage = temp_storage.find_program(program_id)
    assert updated_program_from_storage is not None
    assert updated_program_from_storage.total_episodes == 2
    assert updated_program_from_storage.updated_at > old_program.updated_at

    # --- 5. Generate the download list ---
    dl_generator = DownloadListGenerator(output_dir=str(output_dir))
    generated_file = dl_generator.generate_download_list(
        updated_program_from_storage,
        diff,
        output_file="download_urls.txt"
    )

    # --- 6. Assertions for the generated file ---
    assert generated_file == download_list_path
    assert download_list_path.exists()
    
    content = download_list_path.read_text("utf-8")
    
    # Check for new episode section
    assert f"# {new_program.title} - New Episodes" in content
    assert "# Episode 2: Episode 2" in content
    assert "https://abema.tv/video/episode/ep2" in content
    
    # Check for premium-to-free section
    assert f"# {new_program.title} - Premium to Free" in content
    assert "https://abema.tv/video/episode/ep1" in content
