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

Audio caching functionality for the speaking clock
"""

import os
from pathlib import Path
from typing import Optional


class AudioCache:
    """Audio cache manager for speaking clock"""
    def __init__(self, cache_dir: str, language: str):
        self.base_dir = Path(os.path.expanduser(cache_dir))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.language = language

    def get_cache_filename(self, voice_id: str, hour: int, minute: int) -> str:
        """
        Get cache filename using the format: LANG-VOICE-HH-MM.mp3 (lowercased)

        Args:
            voice_id: ElevenLabs voice ID or name
            hour: Hour (00-23)
            minute: Minute (00-59)

        Returns:
            Cache filename
        """
        return f"{self.language}-{voice_id}-{hour:02d}-{minute:02d}.mp3".lower()

    def get_cached_file_path(self, voice_id: str, hour: int, minute: int) -> Path:
        """Get full path for a cached audio file"""
        filename = self.get_cache_filename(voice_id, hour, minute)
        return self.base_dir / filename

    def get_cached_audio(self, voice_id: str, hour: int, minute: int) -> Optional[Path]:
        """
        Get cached audio file if it exists

        Args:
            voice_id: ElevenLabs voice ID
            hour: Hour (0-23)
            minute: Minute (0-59)

        Returns:
            Path to cached file or None if not found
        """
        cache_path = self.get_cached_file_path(voice_id, hour, minute)
        return cache_path if cache_path.exists() else None

    def save_audio(self, audio_data: bytes, voice_id: str, hour: int, minute: int) -> Path:
        """
        Save audio data to cache

        Args:
            audio_data: Audio data bytes
            voice_id: ElevenLabs voice ID
            hour: Hour (0-23)
            minute: Minute (0-59)

        Returns:
            Path to cached file
        """
        cache_path = self.get_cached_file_path(voice_id, hour, minute)
        with open(cache_path, 'wb') as file:
            file.write(audio_data)

        return cache_path
