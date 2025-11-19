import pytest
from datetime import datetime, timedelta
from abm_check.domain.models import Program, Episode
from abm_check.infrastructure.storage import ProgramStorage
from abm_check.infrastructure.fetcher import BaseFetcher, AbemaFetcher

def test_program_platform_field():
    """Test platform field in Program model."""
    now = datetime.now()
    program = Program(
        id="test-id",
        title="Test Program",
        description="Desc",
        url="http://example.com",
        thumbnail_url="http://example.com/img",
        total_episodes=1,
        latest_episode_number=1,
        episodes=[],
        fetched_at=now,
        updated_at=now,
        platform="tver"
    )
    assert program.platform == "tver"

def test_episode_expiration_date_field():
    """Test expiration_date field in Episode model."""
    exp_date = datetime.now() + timedelta(days=7)
    episode = Episode(
        id="ep-1",
        number=1,
        title="Ep 1",
        description="Desc",
        duration=100,
        thumbnail_url="http://example.com/img",
        is_downloadable=True,
        is_premium_only=False,
        download_url="http://example.com/dl",
        formats=[],
        upload_date="20230101",
        expiration_date=exp_date
    )
    assert episode.expiration_date == exp_date

def test_storage_platform_persistence(tmp_path):
    """Test saving and loading program with platform field."""
    data_file = tmp_path / "programs.yaml"
    storage = ProgramStorage(data_file=str(data_file))
    
    now = datetime.now()
    program = Program(
        id="test-id",
        title="Test Program",
        description="Desc",
        url="http://example.com",
        thumbnail_url="http://example.com/img",
        total_episodes=1,
        latest_episode_number=1,
        episodes=[],
        fetched_at=now,
        updated_at=now,
        platform="niconico"
    )
    
    storage.save_program(program)
    loaded_programs = storage.load_programs()
    
    assert len(loaded_programs) == 1
    assert loaded_programs[0].platform == "niconico"

def test_storage_expiration_date_persistence(tmp_path):
    """Test saving and loading episode with expiration_date."""
    data_file = tmp_path / "programs.yaml"
    storage = ProgramStorage(data_file=str(data_file))
    
    exp_date = datetime.now().replace(microsecond=0) # YAML serialization might lose microsecond precision depending on implementation
    episode = Episode(
        id="ep-1",
        number=1,
        title="Ep 1",
        description="Desc",
        duration=100,
        thumbnail_url="http://example.com/img",
        is_downloadable=True,
        is_premium_only=False,
        download_url="http://example.com/dl",
        formats=[],
        upload_date="20230101",
        expiration_date=exp_date
    )
    
    now = datetime.now()
    program = Program(
        id="test-id",
        title="Test Program",
        description="Desc",
        url="http://example.com",
        thumbnail_url="http://example.com/img",
        total_episodes=1,
        latest_episode_number=1,
        episodes=[episode],
        fetched_at=now,
        updated_at=now,
        platform="abema"
    )
    
    storage.save_program(program)
    loaded_programs = storage.load_programs()
    
    loaded_ep = loaded_programs[0].episodes[0]
    assert loaded_ep.expiration_date == exp_date

def test_fetcher_abstraction():
    """Test that AbemaFetcher inherits from BaseFetcher."""
    assert issubclass(AbemaFetcher, BaseFetcher)
    
    fetcher = AbemaFetcher()
    assert isinstance(fetcher, BaseFetcher)
