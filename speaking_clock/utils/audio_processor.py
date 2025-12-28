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

Audio processing utilities for the speaking clock
"""

import io
import numpy as np
from typing import Optional

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    import soundfile as sf
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


def adjust_volume(audio_data: bytes, volume: float = 1.0) -> bytes:
    """
    Adjust the volume of audio data in memory, without modifying source files

    Args:
        audio_data: Audio data in bytes
        volume: Volume level from 0.0 to 1.0

    Returns:
        Adjusted audio data in bytes, or original audio if processing failed
    """
    # Validate volume level
    volume = max(0.0, min(1.0, volume))

    # If volume is 1.0 or very close, no adjustment needed
    if abs(volume - 1.0) < 0.01:
        return audio_data

    # Try using pydub if available
    if PYDUB_AVAILABLE:
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            # Convert volume factor to dB change
            # 0.0 = -96dB, 0.5 = -6dB, 1.0 = 0dB
            if volume <= 0.001:  # Avoid extreme low values
                db_change = -96  # Near silence
            else:
                db_change = 20 * np.log10(volume)
            adjusted_audio = audio.apply_gain(db_change)

            # Export back to bytes
            buffer = io.BytesIO()
            adjusted_audio.export(buffer, format="mp3")
            return buffer.getvalue()
        except Exception as e:
            print(f"Warning: Pydub volume adjustment failed: {e}")
            # Fall through to the next method

    # Try using librosa and soundfile if available
    if LIBROSA_AVAILABLE:
        try:
            # Load audio data into numpy array
            with io.BytesIO(audio_data) as buffer:
                y, sr = librosa.load(buffer, sr=None)

            # Adjust volume by scaling the waveform
            y_adjusted = y * volume

            # Save back to bytes
            buffer = io.BytesIO()
            sf.write(buffer, y_adjusted, sr, format='mp3')
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            print(f"Warning: Librosa volume adjustment failed: {e}")

    # If all methods failed and we have no library support, warn once
    if not PYDUB_AVAILABLE and not LIBROSA_AVAILABLE:
        print("Warning: Cannot adjust volume. Install pydub or librosa+soundfile for volume control.")

    # Return original audio data as fallback
    return audio_data
