import pytest
from unittest.mock import MagicMock, patch
from abm_check.infrastructure.fetchers.tver import TVerFetcher
from abm_check.domain.exceptions import FetchError, YtdlpError

@pytest.fixture
def tver_fetcher():
    config = MagicMock()
    config.cache_dir = "dummy_cache"
    config.ytdlp_opts = {}
    config.cache_ttl = 3600
    return TVerFetcher(config=config)

def test_fetch_program_info_success(tver_fetcher):
    """Test successful fetching of TVer program info."""
    mock_info = {
        'id': 'sr12345',
        'title': 'Test Series',
        'description': 'Test Description',
        'webpage_url': 'https://tver.jp/series/sr12345',
        'thumbnail': 'http://example.com/thumb.jpg',
        'entries': [
            {
                'id': 'ep1',
                'episode_number': 1,
                'title': 'Episode 1',
                'description': 'Ep 1 Desc',
                'duration': 1200,
                'thumbnail': 'http://example.com/ep1.jpg',
                'webpage_url': 'https://tver.jp/episodes/ep1',
                'formats': [{'format_id': 'f1', 'url': 'http://video.mp4'}],
                'upload_date': '20230101'
            }
        ]
    }

    with patch('yt_dlp.YoutubeDL') as mock_ydl_cls:
        mock_ydl = mock_ydl_cls.return_value
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = mock_info
        
        # Mock cache methods to avoid file I/O
        with patch.object(tver_fetcher, '_load_cache', return_value=None):
            with patch.object(tver_fetcher, '_save_cache'):
                program = tver_fetcher.fetch_program_info('sr12345')

    assert program.id == 'sr12345'
    assert program.title == 'Test Series'
    assert program.platform == 'tver'
    assert len(program.episodes) == 1
    assert program.episodes[0].id == 'ep1'
    assert program.episodes[0].number == 1

def test_fetch_program_info_ytdlp_error(tver_fetcher):
    """Test handling of yt-dlp errors."""
    with patch('yt_dlp.YoutubeDL') as mock_ydl_cls:
        mock_ydl = mock_ydl_cls.return_value
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("yt-dlp error")
        
        with patch.object(tver_fetcher, '_load_cache', return_value=None):
            with pytest.raises(YtdlpError):
                tver_fetcher.fetch_program_info('sr12345')

def test_fetch_program_info_no_entries(tver_fetcher):
    """Test handling of empty entries."""
    mock_info = {
        'id': 'sr12345',
        'title': 'Test Series',
        'entries': []
    }

    with patch('yt_dlp.YoutubeDL') as mock_ydl_cls:
        mock_ydl = mock_ydl_cls.return_value
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = mock_info
        
        with patch.object(tver_fetcher, '_load_cache', return_value=None):
            with patch.object(tver_fetcher, '_save_cache'):
                program = tver_fetcher.fetch_program_info('sr12345')

    assert program.total_episodes == 0
