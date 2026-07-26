#!/bin/bash

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

# Run from the repo root regardless of where the script was invoked from.
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

# Function to extract the version from pyproject.toml (the single source of truth)
extract_version() {
    local -r project_file="pyproject.toml"
    if [ ! -f "$project_file" ]; then
        echo "*** File not found: ${project_file}"
        exit 1
    fi
    sed -n 's/^version *= *["'\'']\([^"'\'']\+\)["'\''].*/\1/p' "$project_file" | head -n 1
}

# Extract version
VERSION=$(extract_version)
echo "Current version: ${VERSION}"

# Check if version was successfully extracted
if [ -z "$VERSION" ]; then
    echo "Error: Failed to extract version from const source file."
    exit 1
fi

# Activate the local venv only when not already inside one.
ACTIVATED=0
if [[ -z "${VIRTUAL_ENV}" ]]; then
    if [ ! -f ".venv/bin/activate" ]; then
        echo "*** No virtualenv found at .venv/ — create one with: python3 -m venv .venv"
        exit 1
    fi
    # shellcheck source=/dev/null
    source .venv/bin/activate
    ACTIVATED=1
fi

python3 -m build
pipx uninstall "speaking-clock"
pipx install "dist/speaking_clock-${VERSION}-py3-none-any.whl"

#    # pip uninstalled speaking-clock
#    pip uninstall --yes "dist/speaking_clock-${VERSION}-py3-none-any.whl" &&
#    pip install "dist/speaking_clock-${VERSION}-py3-none-any.whl"

if [[ ${ACTIVATED} -eq 1 ]]; then
    deactivate
fi
