"""Unit tests for configuration."""

from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
import yaml

from abm_check.config import Config, get_config


class TestConfig:
    """Test Config class."""

    def test_config_default_values(self) -> None:
        """Test that default configuration values are loaded correctly."""
        config = Config()
        
        assert config.season_threshold == 12
        assert config.max_seasons == 10
        assert config.base_url == "https://abema.tv/video/title"
        assert config.episode_base_url == "https://abema.tv/video/episode"
        assert config.programs_file == "programs.yaml"
        assert config.output_dir == "output"

    def test_config_from_yaml_file(self, tmp_path: Path) -> None:
        """Test loading configuration from YAML file."""
        config_file = tmp_path / "abm_check.yaml"
        config_data = {
            "season_detection": {
                "threshold": 15,
                "max_seasons": 5,
            },
            "storage": {
                "programs_file": "custom_programs.yaml",
                "output_dir": "custom_output",
            },
        }
        
        config_file.write_text(yaml.safe_dump(config_data), encoding="utf-8")
        
        config = Config(str(config_file))
        
        assert config.season_threshold == 15
        assert config.max_seasons == 5
        assert config.programs_file == "custom_programs.yaml"
        assert config.output_dir == "custom_output"

    def test_config_partial_override(self, tmp_path: Path) -> None:
        """Test that partial configuration overrides defaults."""
        config_file = tmp_path / "abm_check.yaml"
        config_data = {
            "season_detection": {
                "threshold": 20,
            },
        }
        
        config_file.write_text(yaml.safe_dump(config_data), encoding="utf-8")
        
        config = Config(str(config_file))
        
        assert config.season_threshold == 20
        assert config.max_seasons == 10

    def test_config_nonexistent_file(self) -> None:
        """Test that non-existent config file falls back to defaults."""
        config = Config("nonexistent.yaml")
        
        assert config.season_threshold == 12
        assert config.max_seasons == 10

    def test_config_get_nested_value(self) -> None:
        """Test getting nested configuration values."""
        config = Config()
        
        assert config.get("season_detection.threshold") == 12
        assert config.get("urls.base_url") == "https://abema.tv/video/title"
        assert config.get("nonexistent.key", "default") == "default"

    def test_config_ytdlp_opts(self) -> None:
        """Test yt-dlp options generation."""
        config = Config()
        opts = config.ytdlp_opts
        
        assert opts["quiet"] is True
        assert opts["no_warnings"] is True
        assert opts["skip_download"] is True
        assert opts["extract_flat"] is False

    def test_config_season_url_pattern(self) -> None:
        """Test season URL pattern generation."""
        config = Config()
        url = config.season_url_pattern.format(program_id="26-249", season=2)
        
        assert "26-249" in url
        assert "s2" in url

    def test_get_config_singleton(self) -> None:
        """Test that get_config returns singleton instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2

    def test_config_invalid_yaml(self, tmp_path: Path) -> None:
        """Test handling of invalid YAML file."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [", encoding="utf-8")
        
        config = Config(str(config_file))
        
        assert config.season_threshold == 12

    @pytest.mark.parametrize("threshold,expected", [
        (5, 5),
        (10, 10),
        (20, 20),
        (100, 100),
    ])
    def test_config_season_threshold_values(self, threshold: int, expected: int, tmp_path: Path) -> None:
        """Test various season threshold values."""
        config_file = tmp_path / "abm_check.yaml"
        config_data = {"season_detection": {"threshold": threshold}}
        config_file.write_text(yaml.safe_dump(config_data), encoding="utf-8")
        
        config = Config(str(config_file))
        assert config.season_threshold == expected

    def test_config_empty_file(self, tmp_path: Path) -> None:
        """Test handling of empty config file."""
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("", encoding="utf-8")
        
        config = Config(str(config_file))
        
        assert config.season_threshold == 12
        assert config.max_seasons == 10
