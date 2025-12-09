"""Tests for DownloadListGenerator."""
import pytest
from pathlib import Path
from abm_check.domain.models import Program, Episode, VideoFormat
from abm_check.infrastructure.updater import EpisodeDiff
from abm_check.infrastructure.download_list import DownloadListGenerator

@pytest.fixture
def test_program(create_program, create_episode) -> Program:
    """Fixture for a standard test program."""
    return create_program("prog-1", [create_episode("ep1", 1)], title="Test Program 1")

def test_generate_download_list_new_episodes(tmp_path, test_program, create_episode):
    """Test generating a list with only new episodes."""
    output_dir = tmp_path / "output"
    output_file = "new.txt"
    
    new_ep = create_episode("ep2", 2, title="The New Episode")
    diff = EpisodeDiff(new_episodes=[new_ep], premium_to_free=[])
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_download_list(test_program, diff, output_file)
    
    assert result_path.exists()
    content = result_path.read_text("utf-8")
    
    assert "# Test Program 1 - New Episodes" in content
    assert "# Episode 2: The New Episode" in content
    assert "https://abema.tv/video/episode/ep2" in content
    assert "Premium to Free" not in content

def test_generate_download_list_premium_to_free(tmp_path, test_program, create_episode):
    """Test generating a list with only premium-to-free episodes."""
    output_dir = tmp_path / "output"
    output_file = "free.txt"
    
    free_ep = create_episode("ep1", 1, title="Now Free!")
    diff = EpisodeDiff(new_episodes=[], premium_to_free=[free_ep])
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_download_list(test_program, diff, output_file)
    
    assert result_path.exists()
    content = result_path.read_text("utf-8")
    
    assert "# Test Program 1 - Premium to Free" in content
    assert "https://abema.tv/video/episode/ep1" in content
    assert "New Episodes" not in content
    assert "# Episode" not in content # No episode title for premium to free

def test_generate_download_list_both_changes(tmp_path, test_program, create_episode):
    """Test generating a list with both new and premium-to-free episodes."""
    output_dir = tmp_path / "output"
    output_file = "both.txt"
    
    new_ep = create_episode("ep2", 2, title="Brand New")
    free_ep = create_episode("ep1", 1, title="Was Premium")
    diff = EpisodeDiff(new_episodes=[new_ep], premium_to_free=[free_ep])
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_download_list(test_program, diff, output_file)
    
    assert result_path.exists()
    content = result_path.read_text("utf-8")
    
    assert "# Test Program 1 - New Episodes" in content
    assert "# Episode 2: Brand New" in content
    assert "https://abema.tv/video/episode/ep2" in content
    
    assert "# Test Program 1 - Premium to Free" in content
    assert "https://abema.tv/video/episode/ep1" in content

def test_generate_download_list_no_changes(tmp_path, test_program):
    """Test generating a list with no changes."""
    output_dir = tmp_path / "output"
    output_file = "no_change.txt"
    
    diff = EpisodeDiff(new_episodes=[], premium_to_free=[])
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_download_list(test_program, diff, output_file)
    
    assert result_path.exists()
    content = result_path.read_text("utf-8").strip()
    assert content == ""

def test_generate_combined_list(tmp_path, create_program, create_episode):
    """Test generating a combined list for multiple programs."""
    output_dir = tmp_path / "output"
    output_file = "combined.txt"
    
    # Program 1: new episode
    prog1 = create_program("prog-1", [], title="My First Show")
    diff1 = EpisodeDiff(new_episodes=[create_episode("p1e1", 1, title="First Ep")], premium_to_free=[])
    
    # Program 2: premium to free
    prog2 = create_program("prog-2", [], title="Another Show")
    diff2 = EpisodeDiff(new_episodes=[], premium_to_free=[create_episode("p2e1", 1)])
    
    # Program 3: no changes
    prog3 = create_program("prog-3", [], title="No Change Show")
    diff3 = EpisodeDiff(new_episodes=[], premium_to_free=[])
    
    updates = {
        "prog-1": (prog1, diff1),
        "prog-2": (prog2, diff2),
        "prog-3": (prog3, diff3),
    }
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_combined_list(updates, output_file)
    
    assert result_path.exists()
    content = result_path.read_text("utf-8")
    
    # Check prog1 content
    assert "# My First Show - New Episodes" in content
    assert "# Episode 1: First Ep" in content
    assert "https://abema.tv/video/episode/p1e1" in content
    
    # Check prog2 content
    assert "# Another Show - Premium to Free" in content
    assert "https://abema.tv/video/episode/p2e1" in content
    
    # Check prog3 content is not present
    assert "No Change Show" not in content

def test_generate_combined_list_no_updates(tmp_path):
    """Test combined list generation when there are no updates."""
    output_dir = tmp_path / "output"
    output_file = "empty_combined.txt"
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_combined_list({}, output_file)
    
    assert result_path is None
    assert not (output_dir / output_file).exists()

def test_generate_download_list_yaml(tmp_path, test_program, create_episode):
    """Test generating a list in YAML format."""
    import yaml
    output_dir = tmp_path / "output"
    output_file = "list.yaml"
    
    new_ep = create_episode("ep2", 2, title="New Ep", duration=1200, thumbnail_url="http://thumb.com/ep2.jpg")
    free_ep = create_episode("ep1", 1, title="Free Ep", duration=1200, thumbnail_url="http://thumb.com/ep1.jpg")
    diff = EpisodeDiff(new_episodes=[new_ep], premium_to_free=[free_ep])
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_download_list(test_program, diff, output_file, format="yaml")
    
    assert result_path.exists()
    
    with open(result_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    assert "entries" in data
    assert len(data["entries"]) == 2
    
    # Check new episode entry
    new_entry = next(e for e in data["entries"] if e["id"] == "ep2")
    assert new_entry["title"] == "New Ep"
    assert new_entry["entry_type"] == "new"
    assert new_entry["thumbnail"] == "http://thumb.com/ep2.jpg"
    assert new_entry["platform"] == "abema"
    
    # Check premium to free entry
    free_entry = next(e for e in data["entries"] if e["id"] == "ep1")
    assert free_entry["title"] == "Free Ep"
    assert free_entry["entry_type"] == "premium_to_free"
    
    # Check metadata
    assert "metadata" in data
    assert data["metadata"]["new_episodes"] == 1
    assert data["metadata"]["premium_to_free"] == 1
    assert data["metadata"]["abm_check_version"] == "1.0.0"

def test_generate_combined_list_yaml(tmp_path, create_program, create_episode):
    """Test generating a combined list in YAML format."""
    import yaml
    output_dir = tmp_path / "output"
    output_file = "combined.yaml"
    
    prog1 = create_program("prog-1", [], title="Show 1")
    diff1 = EpisodeDiff(new_episodes=[create_episode("p1e1", 1)], premium_to_free=[])
    
    prog2 = create_program("prog-2", [], title="Show 2")
    diff2 = EpisodeDiff(new_episodes=[], premium_to_free=[create_episode("p2e1", 1)])
    
    updates = {
        "prog-1": (prog1, diff1),
        "prog-2": (prog2, diff2),
    }
    
    generator = DownloadListGenerator(output_dir=str(output_dir))
    result_path = generator.generate_combined_list(updates, output_file, format="yaml")
    
    assert result_path.exists()
    
    with open(result_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    assert len(data["entries"]) == 2
    assert data["metadata"]["total_entries"] == 2
    assert data["metadata"]["new_episodes"] == 1
    assert data["metadata"]["premium_to_free"] == 1
