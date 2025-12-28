"""
##################################################################################
#
# ▄▀▀▄                █     ▀                ▄▀▀▄ ▀█            █
# ▀▄▄  █▀▀▄ ▄▀▀▄ ▄▀▀▄ █ ▄▀ ▀█  █▀▀▄ ▄▀▀█     █     █  ▄▀▀▄ ▄▀▀▄ █ ▄▀
#    █ █  █ █▀▀   ▄▄█ █▀▄   █  █  █ █  █     █     █  █  █ █    █▀▄
# ▀▄▄▀ █▄▄▀ ▀▄▄▀ ▀▄▄▀ █  █ ▄█▄ █  █ ▀▄▄█     ▀▄▄▀ ▄█▄ ▀▄▄▀ ▀▄▄▀ █  █
#      █                             ▄▄▀
#
# @project   Speaking Clock - time announcer using ElevenLabs TTS API
# @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
# @copyright 2025 Marcin Orlowski
# @license   https://www.opensource.org/licenses/mit-license.php MIT
# @link      https://github.com/MarcinOrlowski/speaking-clock
#
##################################################################################

Configuration management for the speaking clock
"""

import os
import sys
from typing import Dict, Any

import yaml

from speaking_clock.const import Const


class ConfigManager():
    """Config manager for the speaking clock application"""

    def __init__(self, config_path: str = None, config_overrides: dict = None):
        # Initialize with default configuration
        self.config = self._get_default_config()

        # Use provided config path or fall back to default
        self.config_path = os.path.expanduser(config_path or Const.DEFAULT_CONFIG_PATH)

        # Try to load user configuration
        user_config = self._try_load_config(self.config_path)

        # If user config was loaded successfully, update defaults with user settings
        if user_config:
            self._update_config(user_config)

        # Apply command-line overrides if any (highest priority)
        if config_overrides:
            self._apply_overrides(config_overrides)

    def _apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """Apply command line overrides to configuration

        Args:
            overrides: Dictionary with override values from command line
        """
        for section, values in overrides.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values"""
        return {
            "language": {
                "code": "pl",
                "use_24h_clock": True
            },
            "elevenlabs": {
                "api_key": "",
                "voice_id": "Bratanek",
                "model_id": "eleven_multilingual_v2"
            },
            "audio": {
                "overlay_speech": True,
                "speech_offset_ms": 1000,
                "volume": 1.0  # Volume level from 0.0 to 1.0
            },
            "chime": {
                "enabled": True,
                "audio_file": "clock-chime.mp3"
            },
            "cache": {
                "directory": Const.DEFAULT_CACHE_DIR
            }
        }

    def _try_load_config(self, config_path: str) -> Dict[str, Any]:
        """Try to load configuration from YAML file, return None if failed"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except (yaml.YAMLError, FileNotFoundError) as e:
            print(f"Notice: Config file not found or invalid at {config_path}: {e}", file=sys.stderr)
            print(f"Using default configuration", file=sys.stderr)
            return None

    def _update_config(self, user_config: Dict[str, Any]) -> None:
        """Update default config with user settings"""
        # Update each section only if it exists
        for section in self.config:
            if section in user_config and isinstance(user_config[section], dict):
                self.config[section].update(user_config[section])

    def get_elevenlabs_api_key(self) -> str:
        """Get ElevenLabs API key from config or environment"""
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            api_key = self.config.get("elevenlabs", {}).get("api_key", None)

        if api_key:
            return api_key
        raise ValueError("No ElevenLabs API key found in config or environment variable.")

    def get_elevenlabs_voice_id(self) -> str:
        """Get voice ID from config"""
        return self.config.get("elevenlabs", {}).get("voice_id", "Bratanek")

    def get_elevenlabs_model_id(self) -> str:
        """Get model ID from config"""
        return self.config.get("elevenlabs", {}).get("model_id", "eleven_multilingual_v2")

    def get_language_code(self) -> str:
        """Get language code from config"""
        return self.config.get("language", {}).get("code", "pl")

    def use_24h_clock(self) -> bool:
        """Check if 24-hour clock should be used"""
        return self.config.get("language", {}).get("use_24h_clock", True)

    def should_play_chime(self) -> bool:
        """Check if a chime should be played before speaking the time"""
        return self.config.get("chime", {}).get("enabled", False)

    def get_chime_file(self) -> str:
        """Get the path to the chime audio file"""
        return self.config.get("chime", {}).get("audio_file", "clock-chime.mp3")

    def should_overlay_speech(self) -> bool:
        """Check if speech should be overlaid on the chime"""
        return self.config.get("audio", {}).get("overlay_speech", True)

    def get_speech_offset_ms(self) -> int:
        """Get the offset in milliseconds for when to start speech after chime"""
        return self.config.get("audio", {}).get("speech_offset_ms", 1000)

    def get_cache_directory(self) -> str:
        """Get the cache directory path"""
        return self.config.get("cache", {}).get("directory", Const.DEFAULT_CACHE_DIR)

    def get_audio_volume(self) -> float:
        """Get the audio volume level (0.0 to 1.0)"""
        return self.config.get("audio", {}).get("volume", 1.0)
