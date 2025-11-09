"""Tests for ProgramUpdater."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from abm_check.domain.models import Program, Episode, VideoFormat
from abm_check.infrastructure.updater import ProgramUpdater, EpisodeDiff

@pytest.fixture
def mock_fetcher():
    with patch('abm_check.infrastructure.updater.AbemaFetcher') as mock:
        yield mock.return_value

@pytest.fixture
def mock_storage():
    with patch('abm_check.infrastructure.updater.ProgramStorage') as mock:
        yield mock.return_value

def test_update_program_no_changes(mock_fetcher, mock_storage, create_episode, create_program):
    """Test update_program with no changes."""
    program_id = "test-1"
    
    # Both old and new programs are identical
    ep1 = create_episode("ep1", 1)
    old_program = create_program(program_id, [ep1])
    new_program = create_program(program_id, [ep1])
    
    mock_storage.find_program.return_value = old_program
    mock_fetcher.fetch_program_info.return_value = new_program
    
    updater = ProgramUpdater()
    diff = updater.update_program(program_id)
    
    assert diff is not None
    assert not diff.new_episodes
    assert not diff.premium_to_free
    mock_storage.save_program.assert_not_called()

def test_update_program_new_episode(mock_fetcher, mock_storage, create_episode, create_program):
    """Test update_program with a new downloadable episode."""
    program_id = "test-2"
    
    ep1 = create_episode("ep1", 1)
    ep2 = create_episode("ep2", 2)
    
    old_program = create_program(program_id, [ep1])
    new_program = create_program(program_id, [ep1, ep2])
    
    mock_storage.find_program.return_value = old_program
    mock_fetcher.fetch_program_info.return_value = new_program
    
    updater = ProgramUpdater()
    diff = updater.update_program(program_id)
    
    assert diff is not None
    assert len(diff.new_episodes) == 1
    assert diff.new_episodes[0].id == "ep2"
    assert not diff.premium_to_free
    mock_storage.save_program.assert_called_once_with(new_program)

def test_update_program_premium_to_free(mock_fetcher, mock_storage, create_episode, create_program):
    """Test update_program when an episode becomes free."""
    program_id = "test-3"
    
    old_ep = create_episode("ep1", 1, is_downloadable=False, is_premium_only=True)
    new_ep = create_episode("ep1", 1, is_downloadable=True, is_premium_only=False)
    
    old_program = create_program(program_id, [old_ep])
    new_program = create_program(program_id, [new_ep])
    
    mock_storage.find_program.return_value = old_program
    mock_fetcher.fetch_program_info.return_value = new_program
    
    updater = ProgramUpdater()
    diff = updater.update_program(program_id)
    
    assert diff is not None
    assert not diff.new_episodes
    assert len(diff.premium_to_free) == 1
    assert diff.premium_to_free[0].id == "ep1"
    mock_storage.save_program.assert_called_once_with(new_program)

def test_update_program_new_and_premium_to_free(mock_fetcher, mock_storage, create_episode, create_program):
    """Test update_program with both new and premium-to-free episodes."""
    program_id = "test-4"
    
    old_ep1 = create_episode("ep1", 1, is_downloadable=False, is_premium_only=True)
    new_ep1 = create_episode("ep1", 1, is_downloadable=True, is_premium_only=False)
    new_ep2 = create_episode("ep2", 2)
    
    old_program = create_program(program_id, [old_ep1])
    new_program = create_program(program_id, [new_ep1, new_ep2])
    
    mock_storage.find_program.return_value = old_program
    mock_fetcher.fetch_program_info.return_value = new_program
    
    updater = ProgramUpdater()
    diff = updater.update_program(program_id)
    
    assert diff is not None
    assert len(diff.new_episodes) == 1
    assert diff.new_episodes[0].id == "ep2"
    assert len(diff.premium_to_free) == 1
    assert diff.premium_to_free[0].id == "ep1"
    mock_storage.save_program.assert_called_once_with(new_program)

def test_update_program_new_premium_episode(mock_fetcher, mock_storage, create_episode, create_program):
    """Test that a new premium-only episode is not detected as a change."""
    program_id = "test-5"
    
    ep1 = create_episode("ep1", 1)
    new_premium_ep = create_episode("ep2", 2, is_downloadable=False, is_premium_only=True)
    
    old_program = create_program(program_id, [ep1])
    new_program = create_program(program_id, [ep1, new_premium_ep])
    
    mock_storage.find_program.return_value = old_program
    mock_fetcher.fetch_program_info.return_value = new_program
    
    updater = ProgramUpdater()
    diff = updater.update_program(program_id)
    
    assert diff is not None
    assert not diff.new_episodes
    assert not diff.premium_to_free
    mock_storage.save_program.assert_not_called()

def test_update_program_not_found(mock_fetcher, mock_storage):
    """Test update_program when the program is not in storage."""
    program_id = "test-nonexistent"
    
    mock_storage.find_program.return_value = None
    
    updater = ProgramUpdater()
    result = updater.update_program(program_id)
    
    assert result is None
    mock_fetcher.fetch_program_info.assert_not_called()
    mock_storage.save_program.assert_not_called()

def test_update_all_programs(mock_fetcher, mock_storage, create_episode, create_program):
    """Test update_all_programs orchestrates updates correctly."""
    # Program 1: new episode
    prog1_id = "prog1"
    prog1_old = create_program(prog1_id, [create_episode("p1e1", 1)])
    prog1_new = create_program(prog1_id, [create_episode("p1e1", 1), create_episode("p1e2", 2)])

    # Program 2: no changes
    prog2_id = "prog2"
    prog2_old = create_program(prog2_id, [create_episode("p2e1", 1)])
    prog2_new = create_program(prog2_id, [create_episode("p2e1", 1)])

    # Program 3: premium to free
    prog3_id = "prog3"
    prog3_old_ep = create_episode("p3e1", 1, is_downloadable=False, is_premium_only=True)
    prog3_new_ep = create_episode("p3e1", 1, is_downloadable=True, is_premium_only=False)
    prog3_old = create_program(prog3_id, [prog3_old_ep])
    prog3_new = create_program(prog3_id, [prog3_new_ep])

    # Mock storage setup
    mock_storage.load_programs.return_value = [prog1_old, prog2_old, prog3_old]
    
    def find_program_side_effect(pid):
        if pid == prog1_id: return prog1_old
        if pid == prog2_id: return prog2_old
        if pid == prog3_id: return prog3_old
        return None
    mock_storage.find_program.side_effect = find_program_side_effect

    # Mock fetcher setup
    def fetch_side_effect(pid):
        if pid == prog1_id: return prog1_new
        if pid == prog2_id: return prog2_new
        if pid == prog3_id: return prog3_new
        return None
    mock_fetcher.fetch_program_info.side_effect = fetch_side_effect
    
    updater = ProgramUpdater()
    results = updater.update_all_programs()
    
    assert len(results) == 2 # prog2 had no changes
    assert prog1_id in results
    assert prog2_id not in results
    assert prog3_id in results
    
    # Check prog1 diff
    assert len(results[prog1_id].new_episodes) == 1
    assert results[prog1_id].new_episodes[0].id == "p1e2"
    
    # Check prog3 diff
    assert len(results[prog3_id].premium_to_free) == 1
    assert results[prog3_id].premium_to_free[0].id == "p3e1"
    
    assert mock_storage.save_program.call_count == 2
    mock_storage.save_program.assert_any_call(prog1_new)
    mock_storage.save_program.assert_any_call(prog3_new)
