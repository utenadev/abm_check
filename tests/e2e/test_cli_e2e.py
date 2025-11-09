"""End-to-end tests for CLI commands."""
import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch

from abm_check.cli.main import cli
from abm_check.domain.models import Program, Episode, VideoFormat

@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()

@pytest.fixture
def work_dir(tmp_path: Path) -> Path:
    """Create a temporary working directory and cd into it."""
    # Create subdirectories for output and config
    (tmp_path / "output").mkdir()
    
    # Yield the temporary path
    yield tmp_path

@patch('abm_check.infrastructure.fetcher.AbemaFetcher.fetch_program_info')
def test_add_and_update_e2e(mock_fetch, runner: CliRunner, work_dir: Path, create_program, create_episode):
    """
    E2E test for 'add' and 'update' commands.
    - Mocks the fetcher to control program data.
    - Runs in an isolated temporary directory.
    """
    program_id = "e2e-test-1"
    
    # --- 1. 'add' command ---
    
    # Define the initial program data
    initial_program = create_program(
        program_id,
        [create_episode("ep1", 1, is_downloadable=False, is_premium_only=True)],
        title="E2E Test Program"
    )
    mock_fetch.return_value = initial_program
    
    # Change to the temporary working directory
    with runner.isolated_filesystem(temp_dir=work_dir) as td:
        # Run the 'add' command
        result_add = runner.invoke(cli, ['add', program_id], catch_exceptions=False)
        
        assert result_add.exit_code == 0
        
        # Verify that files were created
        programs_yaml = Path("programs.yaml")
        program_md = Path("output") / program_id / "program.md"
        
        assert programs_yaml.exists()
        assert program_md.exists()
        
        # Verify content of program.md
        md_content = program_md.read_text("utf-8")
        assert "# E2E Test Program" in md_content
        assert "🔒" in md_content # Premium episode
        
        # --- 2. 'update' command ---
        
        # Define the updated program data
        updated_program = create_program(
            program_id,
            [
                create_episode("ep1", 1, is_downloadable=True, is_premium_only=False), # Now free
                create_episode("ep2", 2, is_downloadable=True)  # New episode
            ],
            title="E2E Test Program"
        )
        mock_fetch.return_value = updated_program
        
        # Run the 'update' command
        result_update = runner.invoke(cli, ['update', program_id], catch_exceptions=False)
        
        assert result_update.exit_code == 0
        assert "Changes detected" in result_update.output
        
        # Verify that the download list was created
        download_list = Path("output") / "download_urls.txt"
        assert download_list.exists()
        
        # Verify content of the download list
        dl_content = download_list.read_text("utf-8")
        assert "# E2E Test Program - New Episodes" in dl_content
        assert "https://abema.tv/video/episode/ep2" in dl_content
        assert "# E2E Test Program - Premium to Free" in dl_content
        assert "https://abema.tv/video/episode/ep1" in dl_content
        
        # Verify that program.md was updated
        updated_md_content = program_md.read_text("utf-8")
        assert "✅" in updated_md_content # Now free
        assert "Episode 2" in updated_md_content
