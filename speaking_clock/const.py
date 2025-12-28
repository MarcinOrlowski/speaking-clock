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

from enum import Enum
from typing import List


class Version(Enum):
    MAJOR = 1
    MINOR = 0
    PATCH = 0

    @classmethod
    def as_string(cls) -> str:
        return f"{cls.MAJOR.value}.{cls.MINOR.value}.{cls.PATCH.value}"


class Const(object):
    APP_NAME: str = 'Speaking Clock'
    APP_PROJECT_NAME: str = 'Speaking Clock'
    APP_VERSION: str = Version.as_string()
    APP_URL: str = 'https://github.com/MarcinOrlowski/speaking-clock/'
    APP_DESCRIPTION: str = 'Tells current time using ElevenLabs Text To Speach API',
    APP_YEAR: int = 2025

    DEFAULT_CONFIG_PATH: str = "~/.config/speaking-clock/config.yml"
    DEFAULT_CACHE_DIR: str = "~/.cache/speaking-clock"

    APP_DESCRIPTION: List[str] = [
        f'{APP_NAME} v{APP_VERSION} * Copyright {APP_YEAR} by Marcin Orlowski.',
        APP_DESCRIPTION,
        APP_URL,
    ]
