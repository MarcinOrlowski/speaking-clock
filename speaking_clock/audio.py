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

import hashlib
import os
from pathlib import Path
from typing import Optional

# How much of the spoken text's digest goes into a cache filename. The full hex digest
# would make for unwieldy names, and the rest of the key already pins language, voice
# and time, so this only has to separate the handful of wordings one time can have.
TEXT_DIGEST_LENGTH = 8


def text_digest(text: str) -> str:
    """
    Get the short digest a cache filename carries for the text it was generated from

    Args:
        text: The text handed to the TTS engine

    Returns:
        Truncated hex digest of the text
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:TEXT_DIGEST_LENGTH]


class AudioCache:
    """Audio cache manager for speaking clock"""
    def __init__(self, cache_dir: str, language: str):
        self.base_dir = Path(os.path.expanduser(cache_dir))
        self.language = language

    def get_cache_filename(self, voice_id: str, hour: int, minute: int, text: str) -> str:
        """
        Get cache filename using the format: LANG-VOICE-HH-MM-DIGEST.mp3 (lowercased)

        The time alone does not determine what gets said: midnight is announced with the
        name of the day, so its wording differs from one day to the next. Keying on the
        digest of the spoken text as well gives each of those wordings its own entry,
        instead of the first one generated being replayed ever after. It also retires
        entries by itself when a language file changes what a time sounds like.

        Args:
            voice_id: ElevenLabs voice ID or name
            hour: Hour (00-23)
            minute: Minute (00-59)
            text: The text the audio was, or will be, generated from

        Returns:
            Cache filename
        """
        digest = text_digest(text)
        return f"{self.language}-{voice_id}-{hour:02d}-{minute:02d}-{digest}.mp3".lower()

    def get_cached_file_path(self, voice_id: str, hour: int, minute: int, text: str) -> Path:
        """Get full path for a cached audio file"""
        filename = self.get_cache_filename(voice_id, hour, minute, text)
        return self.base_dir / filename

    def get_cached_audio(self, voice_id: str, hour: int, minute: int,
                         text: str) -> Optional[Path]:
        """
        Get cached audio file if it exists

        Args:
            voice_id: ElevenLabs voice ID
            hour: Hour (0-23)
            minute: Minute (0-59)
            text: The text the audio was generated from

        Returns:
            Path to cached file or None if not found
        """
        cache_path = self.get_cached_file_path(voice_id, hour, minute, text)
        return cache_path if cache_path.exists() else None

    def save_audio(self, audio_data: bytes, voice_id: str, hour: int, minute: int,
                   text: str) -> Path:
        """
        Save audio data to cache

        Args:
            audio_data: Audio data bytes
            voice_id: ElevenLabs voice ID
            hour: Hour (0-23)
            minute: Minute (0-59)
            text: The text the audio was generated from

        Returns:
            Path to cached file
        """
        cache_path = self.get_cached_file_path(voice_id, hour, minute, text)
        # Created on first write so a cache-disabled run leaves no empty directory behind
        self.base_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'wb') as file:
            file.write(audio_data)

        return cache_path
