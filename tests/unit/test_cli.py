"""Tests for CLI commands."""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from abm_check.cli.main import cli
from abm_check.domain.models import Program, Episode
from abm_check.infrastructure.updater import EpisodeDiff
from abm_check.domain.exceptions import AbmCheckError

@pytest.fixture
def runner():
    return CliRunner()

# We patch all infrastructure classes used by the CLI commands
@pytest.fixture(autouse=True)
def mock_infra():
    with patch('abm_check.cli.main.ProgramStorage') as ms, \
         patch('abm_check.cli.main.MarkdownGenerator') as mmg, \
         patch('abm_check.cli.main.ProgramUpdater') as mu, \
         patch('abm_check.cli.main.DownloadListGenerator') as mdlg:

        yield {
            "storage": ms.return_value,
            "md_gen": mmg.return_value,
            "updater": mu.return_value,
            "dl_gen": mdlg.return_value
        }

def test_add_command_success(runner, mock_infra, create_program, create_episode):
    """Test the 'add' command for a successful case."""
    program_id = "26-249"
    mock_program = create_program(program_id, [create_episode("ep1", 1)], title="Test Program")
    
    with patch('abm_check.infrastructure.fetcher_factory.FetcherFactory.create_fetcher') as mock_create:
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_program_info.return_value = mock_program
        mock_create.return_value = (mock_fetcher, program_id)
        
        result = runner.invoke(cli, ['add', program_id])
        
        mock_fetcher.fetch_program_info.assert_called_once_with(program_id)
        mock_infra["storage"].save_program.assert_called_once_with(mock_program)
        mock_infra["md_gen"].save_program_md.assert_called_once_with(mock_program)
        assert result.exit_code == 0

def test_add_command_with_url(runner, mock_infra, create_program):
    """Test the 'add' command using a full URL."""
    program_id = "26-249"
    url = f"https://abema.tv/video/title/{program_id}"
    mock_program = create_program(program_id, [], title="URL Program")
    
    with patch('abm_check.infrastructure.fetcher_factory.FetcherFactory.create_fetcher') as mock_create:
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_program_info.return_value = mock_program
        mock_create.return_value = (mock_fetcher, program_id)
        
        result = runner.invoke(cli, ['add', url])
        
        mock_fetcher.fetch_program_info.assert_called_once_with(program_id)
        assert result.exit_code == 0

def test_add_command_failure(runner, mock_infra):
    """Test the 'add' command when an error occurs."""
    program_id = "26-249"
    
    with patch('abm_check.infrastructure.fetcher_factory.FetcherFactory.create_fetcher') as mock_create:
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_program_info.side_effect = AbmCheckError("Fetch failed")
        mock_create.return_value = (mock_fetcher, program_id)
        
        result = runner.invoke(cli, ['add', program_id])
        
        assert '[ERROR] Failed to add program: Fetch failed' in result.output
        assert result.exit_code == 1

@pytest.mark.parametrize(
    "invalid_id",
    [
        "https://unknown-site.com/invalid",
    ],
)
def test_add_command_invalid_id(runner, mock_infra, invalid_id):
    """Test the 'add' command with invalid program IDs."""
    with patch('abm_check.infrastructure.fetcher_factory.FetcherFactory.create_fetcher') as mock_create:
        mock_create.side_effect = ValueError("Invalid URL/ID")
        
        result = runner.invoke(cli, ['add', invalid_id])
        
        assert result.exit_code == 1
        assert "Invalid URL/ID" in result.output


def test_list_command_success(runner, mock_infra, create_program):
    """Test the 'list' command with existing programs."""
    prog1 = create_program("p1", [], title="Program 1")
    prog2 = create_program("p2", [], title="Program 2")
    mock_infra["storage"].load_programs.return_value = [prog1, prog2]
    
    result = runner.invoke(cli, ['list'])
    
    assert "p1 Program 1" in result.output
    assert result.exit_code == 0

def test_list_command_empty(runner, mock_infra):
    """Test the 'list' command when no programs are stored."""
    mock_infra["storage"].load_programs.return_value = []
    
    result = runner.invoke(cli, ['list'])
    
    assert result.exit_code == 0

@patch('pathlib.Path')
def test_view_command_success(MockPath, runner, mock_infra):
    """Test the 'view' command."""
    program_id = "view-prog"
    md_content = "# View Me"
    
    mock_file = MagicMock()
    mock_file.exists.return_value = True
    mock_file.read_text.return_value = md_content
    MockPath.return_value.__truediv__.return_value.__truediv__.return_value = mock_file
    
    result = runner.invoke(cli, ['view', program_id])
    
    assert result.exit_code == 0

def test_update_command_single_program_with_changes(runner, mock_infra, create_program, create_episode):
    """Test 'update' for a single program with detected changes."""
    program_id = "update-prog"
    mock_program = create_program(program_id, [], title="Update Me")
    diff = EpisodeDiff(new_episodes=[create_episode("ep2", 2)], premium_to_free=[])
    
    mock_infra["updater"].update_program.return_value = diff
    mock_infra["storage"].find_program.return_value = mock_program
    
    result = runner.invoke(cli, ['update', program_id])
    
    mock_infra["updater"].update_program.assert_called_once_with(program_id)
    mock_infra["md_gen"].save_program_md.assert_called_once_with(mock_program)
    mock_infra["dl_gen"].generate_download_list.assert_called_once()
    assert result.exit_code == 0

def test_update_command_no_changes(runner, mock_infra):
    """Test 'update' for a single program with no changes."""
    program_id = "no-change-prog"
    diff = EpisodeDiff(new_episodes=[], premium_to_free=[])
    
    mock_infra["updater"].update_program.return_value = diff
    
    result = runner.invoke(cli, ['update', program_id])
    assert result.exit_code == 0

def test_update_all_programs_success(runner, mock_infra, create_program, create_episode):
    """Test 'update' for all programs."""
    prog1 = create_program("p1", [], title="Prog 1")
    diff1 = EpisodeDiff(new_episodes=[create_episode("p1e2", 2)], premium_to_free=[])

    mock_infra["updater"].update_all_programs.return_value = {"p1": diff1}
    mock_infra["storage"].find_program.return_value = prog1

    result = runner.invoke(cli, ['update'])

    mock_infra["updater"].update_all_programs.assert_called_once()
    mock_infra["dl_gen"].generate_combined_list.assert_called_once()
    assert '[INFO] Updated 1 programs' in result.output
    assert result.exit_code == 0

def test_cli_with_data_file_option(runner, mock_infra, create_program, create_episode):
    """Test all commands with --data-file option."""
    program_id = "26-249"
    custom_file = "custom_programs.yaml"
    mock_program = create_program(program_id, [create_episode("ep1", 1)], title="Test Program")

    # Test 'add' command with --data-file
    with patch('abm_check.infrastructure.fetcher_factory.FetcherFactory.create_fetcher') as mock_create:
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_program_info.return_value = mock_program
        mock_create.return_value = (mock_fetcher, program_id)
        
        result = runner.invoke(cli, ['--data-file', custom_file, 'add', program_id])
        
        # Check that the CLI output includes the custom file name
        assert "custom_programs.yaml" in result.output

    # Test 'list' command with --data-file
    mock_infra["storage"].load_programs.return_value = [mock_program]
    result = runner.invoke(cli, ['--data-file', custom_file, 'list'])
    assert program_id in result.output
    assert result.exit_code == 0

    # Reset the mock
    mock_infra["storage"].reset_mock()

    # Test 'update' command with --data-file
    from abm_check.infrastructure.updater import EpisodeDiff
    diff = EpisodeDiff(new_episodes=[create_episode("ep2", 2)], premium_to_free=[])
    mock_infra["updater"].update_program.return_value = diff
    mock_infra["storage"].find_program.return_value = mock_program
    result = runner.invoke(cli, ['--data-file', custom_file, 'update', program_id])
    assert result.exit_code == 0

