import pytest
from unittest.mock import MagicMock, patch, Mock
from abm_check.infrastructure.fetchers.nico import NicoFetcher
from abm_check.domain.exceptions import FetchError


@pytest.fixture
def nico_fetcher():
    config = MagicMock()
    config.cache_dir = "dummy_cache"
    config.ytdlp_opts = {}
    config.cache_ttl = 3600
    return NicoFetcher(config=config)


def test_fetch_program_info_success(nico_fetcher):
    """Test successful fetching of Nicovideo program info using RSS."""
    # Mock RSS feed
    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.feed = {
        'title': 'Test Channel',
        'description': 'Test Description'
    }
    mock_feed.entries = [
        {'link': 'https://www.nicovideo.jp/watch/so12345'},
        {'link': 'https://www.nicovideo.jp/watch/so12346'}
    ]
    
    # Mock yt-dlp response
    mock_video_info = {
        'id': 'so12345',
        'title': 'Test Video',
        'description': 'Video description',
        'duration': 600,
        'thumbnail': 'http://example.com/thumb.jpg',
        'webpage_url': 'https://www.nicovideo.jp/watch/so12345',
        'formats': [{'format_id': 'f1', 'url': 'http://video.mp4'}],
        'upload_date': '20230101',
        'availability': 'public',
        'episode_number': 1
    }

    with patch('feedparser.parse', return_value=mock_feed):
        with patch('yt_dlp.YoutubeDL') as mock_ydl_cls:
            mock_ydl = mock_ydl_cls.return_value
            mock_ydl.__enter__.return_value = mock_ydl
            mock_ydl.extract_info.return_value = mock_video_info
            
            with patch.object(nico_fetcher, '_load_cache', return_value=None):
                with patch.object(nico_fetcher, '_save_cache'):
                    program = nico_fetcher.fetch_program_info('testchannel')

    assert program.id == 'testchannel'
    assert program.title == 'Test Channel'
    assert program.platform == 'niconico'
    assert len(program.episodes) > 0


def test_fetch_program_info_rss_error(nico_fetcher):
    """Test handling of RSS parsing errors."""
    mock_feed = Mock()
    mock_feed.bozo = True
    mock_feed.entries = []
    mock_feed.bozo_exception = Exception("RSS parse error")
    
    with patch('feedparser.parse', return_value=mock_feed):
        with patch.object(nico_fetcher, '_load_cache', return_value=None):
            with pytest.raises(FetchError):
                nico_fetcher.fetch_program_info('testchannel')


def test_fetch_program_info_no_videos(nico_fetcher):
    """Test handling of RSS with no video links."""
    mock_feed = Mock()
    mock_feed.bozo = False
    mock_feed.entries = [
        {'link': 'https://example.com/invalid'}
    ]
    
    with patch('feedparser.parse', return_value=mock_feed):
        with patch.object(nico_fetcher, '_load_cache', return_value=None):
            with pytest.raises(FetchError):
                nico_fetcher.fetch_program_info('testchannel')
