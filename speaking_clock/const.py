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

import re
from importlib.metadata import PackageNotFoundError, version as _distribution_version
from pathlib import Path
from typing import List

# The version lives in pyproject.toml and nowhere else. Installed builds read it back from
# the distribution metadata; source checkouts (python -m speaking_clock.cli) fall back to
# parsing pyproject.toml, which sits one level above this package.
_PYPROJECT_VERSION_RE = re.compile(r'^version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def _resolve_version() -> str:
    try:
        return _distribution_version('speaking-clock')
    except PackageNotFoundError:
        pyproject = Path(__file__).resolve().parent.parent / 'pyproject.toml'
        try:
            match = _PYPROJECT_VERSION_RE.search(pyproject.read_text(encoding='utf-8'))
        except OSError:
            return 'unknown'
        return match.group(1) if match else 'unknown'


class Const(object):
    APP_NAME: str = 'Speaking Clock'
    APP_PROJECT_NAME: str = 'Speaking Clock'
    APP_VERSION: str = _resolve_version()
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
