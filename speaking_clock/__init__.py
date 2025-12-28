"""
Speaking Clock - A Python package that speaks the current time
using ElevenLabs API and caches audio for reuse
"""

from .clock import SpeakingClock
from .config import ConfigManager
from .audio import AudioCache
from .utils.number_converter import PolishTimeFormatter, PolishNumberConverter

__version__ = "0.1.0"
__author__ = "Carlos"
__email__ = "carlos@example.com"

# Expose main function for easy imports
def speak_time():
    """Main entry point to speak the current time"""
    SpeakingClock().speak_time()
