"""
Speaking Clock - A Python package that speaks the current time
using ElevenLabs API and caches audio for reuse
"""

from .clock import SpeakingClock
from .config import ConfigManager
from .audio import AudioCache
from .const import Const
from .utils.number_converter import PolishTimeFormatter, PolishNumberConverter

__version__ = Const.APP_VERSION
__author__ = "Marcin Orlowski"
__email__ = "mail@marcinorlowski.com"

# Expose main function for easy imports
def speak_time():
    """Main entry point to speak the current time"""
    SpeakingClock().speak_time()
