"""
Data package for speaking-clock
"""

import os
import importlib.resources as pkg_resources

# Define paths to data files relative to this package
DATA_DIR = os.path.dirname(__file__)
DEFAULT_CONFIG_PATH = os.path.join(DATA_DIR, "defaults", "config.yml")
CHIME_FILE_PATH = os.path.join(DATA_DIR, "clock-chime.mp3")
