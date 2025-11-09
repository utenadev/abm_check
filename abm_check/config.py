"""Configuration management for abm_check."""
import os
from pathlib import Path
from typing import Optional
import yaml


class Config:
    """Configuration for abm_check."""
    
    DEFAULT_CONFIG = {
        'season_detection': {
            'threshold': 12,
            'max_seasons': 10,
        },
        'urls': {
            'base_url': 'https://abema.tv/video/title',
            'episode_base_url': 'https://abema.tv/video/episode',
            'season_url_pattern': 'https://abema.tv/video/title/{program_id}?s={program_id}_s{season}&eg={program_id}_eg0',
        },
        'storage': {
            'programs_file': 'programs.yaml',
            'output_dir': 'output',
        },
        'ytdlp': {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
        },
        'cache': {
            'cache_dir': '.cache',
            'cache_ttl': 3600, # seconds (1 hour)
        },
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to config file (optional)
        """
        import copy
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
        
        if config_file and Path(config_file).exists():
            self._load_config(config_file)
        elif config_file is None:
            default_config_path = Path('abm_check.yaml')
            if default_config_path.exists():
                self._load_config(str(default_config_path))
    
    def _load_config(self, config_file: str):
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._merge_config(user_config)
        except Exception:
            pass
    
    def _merge_config(self, user_config: dict):
        """Merge user configuration with defaults."""
        for key, value in user_config.items():
            if key in self.config and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default=None):
        """
        Get configuration value.
        
        Args:
            key: Dot-separated key path (e.g., 'season_detection.threshold')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def season_threshold(self) -> int:
        """Get season detection threshold."""
        return self.get('season_detection.threshold', 12)
    
    @property
    def max_seasons(self) -> int:
        """Get maximum number of seasons to detect."""
        return self.get('season_detection.max_seasons', 10)
    
    @property
    def base_url(self) -> str:
        """Get base URL for programs."""
        return self.get('urls.base_url', 'https://abema.tv/video/title')
    
    @property
    def episode_base_url(self) -> str:
        """Get base URL for episodes."""
        return self.get('urls.episode_base_url', 'https://abema.tv/video/episode')
    
    @property
    def season_url_pattern(self) -> str:
        """Get season URL pattern."""
        return self.get('urls.season_url_pattern', 
                       'https://abema.tv/video/title/{program_id}?s={program_id}_s{season}&eg={program_id}_eg0')
    
    @property
    def programs_file(self) -> str:
        """Get programs database file path."""
        return self.get('storage.programs_file', 'programs.yaml')
    
    @property
    def output_dir(self) -> str:
        """Get output directory path."""
        return self.get('storage.output_dir', 'output')
    
    @property
    def ytdlp_opts(self) -> dict:
        """Get yt-dlp options."""
        return self.get('ytdlp', {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
        })

    @property
    def cache_dir(self) -> str:
        """Get cache directory path."""
        return self.get('cache.cache_dir', '.cache')

    @property
    def cache_ttl(self) -> int:
        """Get cache Time-To-Live in seconds."""
        return self.get('cache.cache_ttl', 3600)


_config_instance: Optional[Config] = None


def get_config(config_file: Optional[str] = None) -> Config:
    """
    Get global configuration instance.
    
    Args:
        config_file: Path to config file (optional)
        
    Returns:
        Config instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_file)
    
    return _config_instance


def reset_config():
    """Reset global configuration instance."""
    global _config_instance
    _config_instance = None
