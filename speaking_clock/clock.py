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
"""

import datetime
import sys
import threading
import time
from pathlib import Path
from typing import Tuple, Optional

from elevenlabs.client import ElevenLabs
from elevenlabs import play

from .audio import AudioCache
from .config import ConfigManager
from .utils.number_converter import PolishTimeFormatter
from .utils.audio_processor import adjust_volume


class SpeakingClock:
    """Main class for speaking clock functionality"""

    def __init__(self, config_path: str = None, config_overrides: dict = None):
        self.config = ConfigManager(config_path, config_overrides)

        language_code = self.config.get_language_code()
        self.time_formatter = PolishTimeFormatter(language_code)

        self.cache = AudioCache(cache_dir=self.config.get_cache_directory(), language=self.config.get_language_code())

        # Initialize ElevenLabs client
        self.el_client = ElevenLabs(api_key=self.config.get_elevenlabs_api_key())

    def get_current_time(self) -> Tuple[int, int]:
        """
        Get current hour and minute

        Returns:
            Tuple of (hour, minute)
        """
        now = datetime.datetime.now()
        hour = now.hour

        # Convert to 12-hour format if needed
        if not self.config.use_24h_clock() and hour > 12:
            hour = hour % 12
            if hour == 0:
                hour = 12

        return hour, now.minute

    def parse_time_string(self, time_str: str) -> Tuple[int, int]:
        """
        Parse time string in format "HH:MM"

        Args:
            time_str: Time string in format "HH:MM"

        Returns:
            Tuple of (hour, minute)

        Raises:
            ValueError: If time_str is not in valid format
        """
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError("Time must be in format HH:MM")

            hour = int(parts[0])
            minute = int(parts[1])

            if hour < 0 or hour > 23:
                raise ValueError("Hour must be between 0 and 23")

            if minute < 0 or minute > 59:
                raise ValueError("Minute must be between 0 and 59")

            # Convert to 12-hour format if needed
            display_hour = hour
            if not self.config.use_24h_clock() and hour > 12:
                display_hour = hour % 12
                if display_hour == 0:
                    display_hour = 12

            return display_hour, minute

        except (ValueError, IndexError) as e:
            if isinstance(e, ValueError) and str(e) in ["Time must be in format HH:MM",
                                                     "Hour must be between 0 and 23",
                                                     "Minute must be between 0 and 59"]:
                raise
            raise ValueError("Time must be in format HH:MM (e.g. 14:30)")

    def format_time_text(self, hour: int, minute: int) -> str:
        """
        Format time as text in Polish

        Args:
            hour: Hour (adjusted for 12/24h format)
            minute: Minute (0-59)

        Returns:
            Time formatted as Polish text
        """
        return self.time_formatter.format_time(hour, minute)

    def generate_speech(self, text: str) -> Optional[bytes]:
        """
        Generate speech using ElevenLabs API

        Args:
            text: Text to convert to speech

        Returns:
            Audio data as bytes or None if generation failed
        """
        try:
            voice_id = self.config.get_elevenlabs_voice_id()
            model_id = self.config.get_elevenlabs_model_id()

            # Check if voice_id is still the default placeholder
            if voice_id == "polish-voice-id" or not voice_id:
                print(
                    "*** Error: You need to set a valid ElevenLabs voice ID in your config.yml file",
                    file=sys.stderr)
                print("*** Available voices:", file=sys.stderr)
                available_voices = self.el_client.voices.get_all()
                for voice in available_voices.voices:
                    print(f"*** - {voice.name}: {voice.voice_id}", file=sys.stderr)
                return None

            # Get the generator from generate and convert to bytes
            audio_generator = self.el_client.generate(
                text=text,
                voice=voice_id,
                model=model_id,
                stream=False  # Ensure we get a single response, not a stream
            )

            # Combine all chunks into one bytes object
            if hasattr(audio_generator, '__iter__'):
                audio_data = b''.join(chunk for chunk in audio_generator)
                return audio_data
            else:
                return audio_generator
        except ValueError as e:
            print(f"*** Error generating speech: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"*** Unexpected error generating speech: {e}", file=sys.stderr)
            return None

    def play_audio_file(self, audio_path: Path) -> None:
        """
        Play audio file using elevenlabs built-in player with volume adjustment

        Args:
            audio_path: Path to the audio file
        """
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()

            # Apply volume adjustment (in memory only, not modifying the file)
            volume = self.config.get_audio_volume()
            adjusted_audio = adjust_volume(audio_data, volume)

            # Play using built-in elevenlabs player
            play(adjusted_audio)
        except Exception as e:
            print(f"*** Error playing audio file: {e}", file=sys.stderr)

    def play_audio_data(self, audio_data: bytes) -> None:
        """
        Play audio data using elevenlabs built-in player with volume adjustment

        Args:
            audio_data: Audio data bytes
        """
        if audio_data:
            try:
                # Apply volume adjustment (in memory only)
                volume = self.config.get_audio_volume()
                adjusted_audio = adjust_volume(audio_data, volume)

                play(adjusted_audio)
            except Exception as e:
                print(f"*** Error playing audio data: {e}", file=sys.stderr)
        else:
            print("*** Cannot play audio: No audio data available", file=sys.stderr)

    def play_chime(self) -> Optional[bytes]:
        """
        Play the chime audio file if enabled in config

        Returns:
            Original chime audio data if successfully loaded, None otherwise
        """
        if not self.config.should_play_chime():
            return None

        chime_file = self.config.get_chime_file()

        # Try to find chime in different locations
        chime_paths = [
            Path(chime_file),  # Current directory
            Path(__file__).parent / "data" / chime_file,  # Package data directory
            Path(__file__).parent.parent / chime_file,  # Project root
        ]

        chime_path = None
        for path in chime_paths:
            if path.exists():
                chime_path = path
                break

        if not chime_path:
            print(f"*** Warning: Chime file not found: {chime_file}", file=sys.stderr)
            return None

        try:
            with open(chime_path, 'rb') as f:
                chime_data = f.read()

            # Only play the chime here if we're not overlaying speech
            # Note: We apply volume adjustment at playback time, not here
            if not self.config.should_overlay_speech():
                volume = self.config.get_audio_volume()
                adjusted_chime = adjust_volume(chime_data, volume)
                play(adjusted_chime)

            # Return the original chime data (not volume adjusted)
            # Volume adjustment will be applied when playing
            return chime_data

        except Exception as e:
            print(f"*** Error loading chime: {e}", file=sys.stderr)
            return None

    def speak_time(self, custom_time: str = None) -> bool:
        """
        Speak the current time or a custom time

        Args:
            custom_time: Optional time string in format "HH:MM"

        Returns:
            True if successful, False if any critical error occurred
        """
        if custom_time:
            try:
                hour, minute = self.parse_time_string(custom_time)
            except ValueError as e:
                print(f"*** Error: {e}", file=sys.stderr)
                return False
        else:
            hour, minute = self.get_current_time()
        time_text = self.format_time_text(hour, minute)

        # Get voice ID and potential cached file path
        voice_id = self.config.get_elevenlabs_voice_id()
        audio_path = self.cache.get_cached_file_path(voice_id, hour, minute)

        # Event to track if speech audio generation is complete
        speech_ready = threading.Event()
        speech_audio_data = None
        speech_error = False

        # Check if we need to generate the speech audio
        speech_needs_generation = not audio_path.exists()

        # Start speech generation in a separate thread if needed
        if speech_needs_generation:
            def generate_audio():
                nonlocal speech_audio_data, speech_error
                try:
                    result = self.generate_speech(time_text)
                    if result is None:
                        speech_error = True
                    else:
                        speech_audio_data = result
                except Exception as e:
                    print(f"*** Unexpected error in speech generation thread: {e}", file=sys.stderr)
                    speech_error = True
                finally:
                    # Always set the event, even on error, to unblock the main thread
                    speech_ready.set()

            gen_thread = threading.Thread(target=generate_audio)
            gen_thread.start()
        else:
            # Load speech audio from cache
            try:
                with open(audio_path, 'rb') as f:
                    speech_audio_data = f.read()
            except Exception as e:
                print(f"*** Error loading cached audio: {e}", file=sys.stderr)
                speech_error = True
            speech_ready.set()

        # This will return the chime data but not play it if overlay is enabled
        chime_data = self.play_chime()

        # Handle speech with or without overlay
        if self.config.should_play_chime() and self.config.should_overlay_speech() and chime_data:
            # Get configured offset in milliseconds
            offset_ms = self.config.get_speech_offset_ms()
            offset_sec = offset_ms / 1000.0

            # Start playing the chime now with volume adjustment
            volume = self.config.get_audio_volume()
            adjusted_chime = adjust_volume(chime_data, volume)

            chime_thread = threading.Thread(
                target=play,
                args=(adjusted_chime,)  # Play adjusted chime in a separate thread
            )
            chime_thread.start()

            start_time = time.time()

            # Wait for speech to be ready, with a timeout
            if not speech_ready.wait(timeout=30):  # Wait up to 30 seconds
                print("*** Timeout waiting for speech generation", file=sys.stderr)
                return False

            # If there was an error in speech generation, stop processing
            if speech_error or speech_audio_data is None:
                print("*** Speech generation failed, cannot continue", file=sys.stderr)
                return False

            # Calculate how much time has passed since we started the chime
            # If speech is ready earlier than the offset, wait until offset time
            elapsed = time.time() - start_time
            if elapsed < offset_sec:
                wait_time = offset_sec - elapsed
                time.sleep(wait_time)

            if speech_needs_generation:
                # Save the original audio to cache (without volume adjustment)
                self.cache.save_audio(speech_audio_data, voice_id, hour, minute)

            # Play the speech with volume adjustment
            volume = self.config.get_audio_volume()
            adjusted_speech = adjust_volume(speech_audio_data, volume)
            play(adjusted_speech)
        else:
            # Standard sequential playback (chime already played in play_chime if enabled)
            # Wait for speech to be ready, with a timeout
            if not speech_ready.wait(timeout=30):  # Wait up to 30 seconds
                print("*** Timeout waiting for speech generation", file=sys.stderr)
                return False

            # If there was an error in speech generation, stop processing
            if speech_error or speech_audio_data is None:
                print("*** Speech generation failed, cannot continue", file=sys.stderr)
                return False

            if speech_needs_generation:
                # Save the original audio to cache (without volume adjustment)
                self.cache.save_audio(speech_audio_data, voice_id, hour, minute)

            # If chime is disabled or overlay is disabled, play speech now with volume adjustment
            if not self.config.should_play_chime() or not self.config.should_overlay_speech():
                volume = self.config.get_audio_volume()
                adjusted_speech = adjust_volume(speech_audio_data, volume)
                play(adjusted_speech)

        return True
