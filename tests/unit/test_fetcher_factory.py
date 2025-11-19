import pytest
from abm_check.infrastructure.fetcher_factory import FetcherFactory
from abm_check.infrastructure.fetchers.tver import TVerFetcher
from abm_check.infrastructure.fetchers.nico import NicoFetcher
from abm_check.infrastructure.fetcher import AbemaFetcher


@pytest.fixture
def factory():
    return FetcherFactory()


def test_create_fetcher_abema_url(factory):
    """Test AbemaTV URL detection."""
    fetcher, program_id = factory.create_fetcher('https://abema.tv/video/title/26-156')
    assert isinstance(fetcher, AbemaFetcher)
    assert program_id == '26-156'


def test_create_fetcher_abema_id(factory):
    """Test AbemaTV ID detection."""
    fetcher, program_id = factory.create_fetcher('26-156')
    assert isinstance(fetcher, AbemaFetcher)
    assert program_id == '26-156'


def test_create_fetcher_tver_url(factory):
    """Test TVer URL detection."""
    fetcher, program_id = factory.create_fetcher('https://tver.jp/series/sr12345')
    assert isinstance(fetcher, TVerFetcher)
    assert program_id == 'sr12345'


def test_create_fetcher_tver_id(factory):
    """Test TVer series ID detection."""
    fetcher, program_id = factory.create_fetcher('sr12345')
    assert isinstance(fetcher, TVerFetcher)
    assert program_id == 'sr12345'


def test_create_fetcher_nico_url(factory):
    """Test Nicovideo URL detection."""
    fetcher, program_id = factory.create_fetcher('https://ch.nicovideo.jp/danime')
    assert isinstance(fetcher, NicoFetcher)
    assert program_id == 'danime'


def test_create_fetcher_nico_channel_name(factory):
    """Test Nicovideo channel name detection."""
    fetcher, program_id = factory.create_fetcher('danime')
    assert isinstance(fetcher, NicoFetcher)
    assert program_id == 'danime'


def test_create_fetcher_invalid_url(factory):
    """Test invalid URL handling."""
    with pytest.raises(ValueError):
        factory.create_fetcher('https://tver.jp/invalidformat')
