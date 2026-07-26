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
import re
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Tuple, Optional

from elevenlabs.client import ElevenLabs
from elevenlabs.core.api_error import ApiError
from elevenlabs.play import play

from .audio import AudioCache
from .config import ConfigManager
from .utils.number_converter import PolishTimeFormatter
from .utils.audio_processor import adjust_volume

# Matches an ElevenLabs voice ID, to tell IDs apart from voice names without an API round-trip.
VOICE_ID_RE = re.compile(r'^[A-Za-z0-9]{20}$')

# Matches what the removed generate() produced by default, so cached MP3s stay byte-comparable.
ELEVENLABS_OUTPUT_FORMAT = 'mp3_44100_128'


def api_error_message(error: ApiError) -> str:
    """
    Extract the human-readable message from an ElevenLabs API error

    str(ApiError) renders the full response including every HTTP header, which buries the
    one line that says what actually went wrong.

    Args:
        error: The error raised by the SDK

    Returns:
        The API's message, falling back to the raw body when it is not shaped as expected
    """
    body = error.body if isinstance(error.body, dict) else {}
    detail = body.get('detail')
    if isinstance(detail, dict):
        return detail.get('message') or detail.get('status') or str(detail)
    return str(detail or error.body)


class SpeakingClock:
    """Main class for speaking clock functionality"""

    def __init__(self, config_path: str = None, config_overrides: dict = None):
        self.config = ConfigManager(config_path, config_overrides)

        language_code = self.config.get_language_code()
        self.time_formatter = PolishTimeFormatter(language_code)

        self.cache = AudioCache(cache_dir=self.config.get_cache_directory(),
                                language=self.config.get_language_code())

        # Initialize ElevenLabs client
        self.el_client = ElevenLabs(api_key=self.config.get_elevenlabs_api_key())
        # Lazily populated name -> voice ID map
        self._voice_id_cache: Optional[Dict[str, str]] = None

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
            if isinstance(e, ValueError) and str(e) in [
                    "Time must be in format HH:MM",
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

    def resolve_voice_id(self, voice: str) -> Optional[str]:
        """
        Resolve a configured voice to an ElevenLabs voice ID

        The SDK's removed generate() accepted either a voice name or a voice ID, while
        text_to_speech.convert() requires an ID. Names are therefore looked up, so configs
        predating the SDK migration (the bundled default is the name "Bratanek") keep working.

        Args:
            voice: Voice ID or voice name from the configuration

        Returns:
            Voice ID, or None if a name was given that the account does not have
        """
        if VOICE_ID_RE.match(voice):
            return voice

        if self._voice_id_cache is None:
            self._voice_id_cache = {
                known.name: known.voice_id
                for known in self.el_client.voices.get_all().voices
                if known.name
            }

        # Stock voices are named "George - Warm, Captivating Storyteller", so an exact match
        # would force that whole string into the config. Accept the leading part instead.
        wanted = voice.strip().lower()
        matches = {
            name: known_id
            for name, known_id in self._voice_id_cache.items()
            if name.lower() == wanted or name.lower().startswith(f'{wanted} ')
        }

        if len(matches) == 1:
            return next(iter(matches.values()))

        if matches:
            print(f"*** Error: '{voice}' matches more than one voice:", file=sys.stderr)
            self.print_voices(matches)
        else:
            print(f"*** Error: No voice named '{voice}' on your ElevenLabs account", file=sys.stderr)
            print("*** Available voices:", file=sys.stderr)
            self.print_voices(self._voice_id_cache)
        return None

    def print_voices(self, voices: Dict[str, str]) -> None:
        """
        List voices on stderr, one per line

        Args:
            voices: Mapping of voice name to voice ID
        """
        for name, known_id in sorted(voices.items()):
            print(f"*** - {name}: {known_id}", file=sys.stderr)

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
                    "*** Error: No valid ElevenLabs voice ID in your config",
                    file=sys.stderr)
                print("*** Available voices:", file=sys.stderr)
                available_voices = self.el_client.voices.get_all()
                for voice in available_voices.voices:
                    print(f"*** - {voice.name}: {voice.voice_id}", file=sys.stderr)
                return None

            resolved_voice_id = self.resolve_voice_id(voice_id)
            if resolved_voice_id is None:
                return None

            # convert() streams the response, so join the chunks into one bytes object.
            audio_chunks = self.el_client.text_to_speech.convert(
                voice_id=resolved_voice_id,
                text=text,
                model_id=model_id,
                output_format=ELEVENLABS_OUTPUT_FORMAT,
            )
            return b''.join(audio_chunks)
        except ValueError as e:
            print(f"*** Error generating speech: {e}", file=sys.stderr)
            return None
        except ApiError as e:
            print(
                f"*** ElevenLabs API error ({e.status_code}): {api_error_message(e)}",
                file=sys.stderr)
            return None
        except Exception as e:
            print(f"*** Unexpected error generating speech: {e}", file=sys.stderr)
            return None

    def at_configured_volume(self, audio_data: bytes) -> bytes:
        """
        Apply the configured playback volume to audio data

        Scaling happens in memory only - cached files always hold the unmodified API
        response, so a volume change never invalidates the cache.

        Args:
            audio_data: Audio data bytes

        Returns:
            Volume-adjusted audio data
        """
        return adjust_volume(audio_data, self.config.get_audio_volume())

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
            print(f"*** Warning: Chime file not found: {chime_file}",
                  file=sys.stderr)
            return None

        try:
            with open(chime_path, 'rb') as f:
                chime_data = f.read()

            # Only play the chime here if we're not overlaying speech
            # Note: We apply volume adjustment at playback time, not here
            if not self.config.should_overlay_speech():
                play(self.at_configured_volume(chime_data))

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
                    print(f"*** Unexpected error in speech generation thread: {e}",
                          file=sys.stderr)
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

            # Adjust before starting the thread: doing it inside would delay the chime by
            # however long the scaling takes, shifting it against the speech offset below.
            adjusted_chime = self.at_configured_volume(chime_data)

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
                print("*** Speech generation failed, cannot continue",
                      file=sys.stderr)
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
            play(self.at_configured_volume(speech_audio_data))
        else:
            # Standard sequential playback (chime already played in play_chime if enabled)
            # Wait for speech to be ready, with a timeout
            if not speech_ready.wait(timeout=30):  # Wait up to 30 seconds
                print("*** Timeout waiting for speech generation", file=sys.stderr)
                return False

            # If there was an error in speech generation, stop processing
            if speech_error or speech_audio_data is None:
                print("*** Speech generation failed, cannot continue",
                      file=sys.stderr)
                return False

            if speech_needs_generation:
                # Save the original audio to cache (without volume adjustment)
                self.cache.save_audio(speech_audio_data, voice_id, hour, minute)

            # If chime is disabled or overlay is disabled, play speech now with volume adjustment
            if not self.config.should_play_chime() or not self.config.should_overlay_speech():
                play(self.at_configured_volume(speech_audio_data))

        return True
