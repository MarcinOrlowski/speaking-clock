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

import os
import re
from importlib.metadata import PackageNotFoundError, version as _distribution_version
from pathlib import Path
from typing import List

# The version lives in pyproject.toml and nowhere else. Installed builds read it back from
# the distribution metadata; source checkouts (python -m speaking_clock.cli) fall back to
# parsing pyproject.toml, which sits one level above this package.
_PYPROJECT_VERSION_RE = re.compile(r'^version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def _version_from_pyproject() -> str:
    pyproject = Path(__file__).resolve().parent.parent / 'pyproject.toml'
    try:
        content = pyproject.read_text(encoding='utf-8')
    except OSError:
        return 'unknown'
    match = _PYPROJECT_VERSION_RE.search(content)
    return match.group(1) if match else 'unknown'


def _resolve_version() -> str:
    try:
        return _distribution_version('speaking-clock')
    except PackageNotFoundError:
        return _version_from_pyproject()


def xdg_cache_home() -> Path:
    """Base directory for user cache data, per XDG Base Directory Specification.

    Honours $XDG_CACHE_HOME when it holds an absolute path, otherwise falls back to
    ~/.cache as the specification mandates for unset, empty or relative values.
    """
    env_value = os.environ.get('XDG_CACHE_HOME', '')
    if env_value and os.path.isabs(env_value):
        return Path(env_value)
    return Path.home() / '.cache'


def default_cache_dir() -> str:
    """Default location of the generated audio cache"""
    return str(xdg_cache_home() / 'speaking-clock')


class Const(object):
    APP_NAME: str = 'Speaking Clock'
    APP_PROJECT_NAME: str = 'Speaking Clock'
    APP_VERSION: str = _resolve_version()
    APP_URL: str = 'https://github.com/MarcinOrlowski/speaking-clock/'
    APP_DESCRIPTION: str = 'Tells current time using ElevenLabs Text To Speach API',
    APP_YEAR: int = 2025

    DEFAULT_CONFIG_PATH: str = "~/.config/speaking-clock/config.yml"
    DEFAULT_CACHE_DIR: str = default_cache_dir()

    APP_DESCRIPTION: List[str] = [
        f'{APP_NAME} v{APP_VERSION} * Copyright {APP_YEAR} by Marcin Orlowski.',
        APP_DESCRIPTION,
        APP_URL,
    ]
