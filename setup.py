#!/usr/bin/env python3
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
#
# python -m venv venv
# source venv/bin/activate
# pip install -r requirements-dev.txt
# python -m build
# # Reinstall the app (do not do "install --upgrade" as cached bytecode can not be updated)
# pip uninstall --yes dist/speaking_clock-1.0.0-py3-none-any.whl
# # intentionally no --upgrade for install to enforce conflict if not uninstalled fully first.
# pip install dist/spaking_clock-1.0.0-py3-none-any.whl
# twine upload dist/*
#
"""

import os
from setuptools import setup, find_packages

# Read the contents of README.md
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="speaking-clock",
    version="1.0.0",
    author="Marcin Orlowski",
    author_email="info@marcinorlowski.com",
    description="A clock that speaks the current time using ElevenLabs API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/speaking-clock",
    packages=find_packages(),
    install_requires=[
        'elevenlabs',
        'PyYAML',
        'python-dateutil',
        'num2words',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'speak-time=speaking_clock.cli:main',
        ],
    },
    package_data={
        'speaking_clock': [
            'data/*.mp3',
            'data/defaults/config.yml',
            'languages/*.yml',
        ],
    },
    include_package_data=True,
)
