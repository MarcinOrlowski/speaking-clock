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


Command-line interface for the speaking clock

Examples:
    # Speak the current time
    speak-time

    # Speak a specific time
    speak-time --time 14:30

    # Short form
    speak-time -t 14:30

    # With custom config
    speak-time -t 08:15 --config ~/my-config.yml

    # Disable the chime
    speak-time --no-chime

    # Enable the chime (overriding config)
    speak-time --chime

    # Set audio volume (0.0 to 1.0)
    speak-time --volume 0.5

    # Combine options
    speak-time -t 08:15 --no-chime --volume 0.8
"""

import argparse
import sys

from speaking_clock.const import Const
from .clock import SpeakingClock


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="Speaking Clock")
    parser.add_argument("--cache",
                        default=Const.DEFAULT_CACHE_DIR,
                        help='Location of file cache. Default: %(default)s')
    parser.add_argument("--config", '-c',
                        default=Const.DEFAULT_CONFIG_PATH,
                        help='Configuration file path. Default: %(default)s')
    parser.add_argument("--time", '-t',
                        help='Specify time in format "HH:MM" (e.g. 14:30). If not provided, current time will be used.')
    # Create a mutually exclusive group for chime options
    chime_group = parser.add_mutually_exclusive_group()
    chime_group.add_argument("--chime",
                            action='store_true',
                            help='Enable the chime sound (overrides config file)')
    chime_group.add_argument("--no-chime",
                            action='store_true',
                            help='Disable the chime sound (overrides config file)')
    parser.add_argument("--volume", '-v',
                        type=float,
                        help='Set audio volume level (0.0 to 1.0)')
    args = parser.parse_args()

    # Prepare command line overrides for config
    config_overrides = {}
    if args.chime:
        config_overrides['audio'] = {'play_chime': True}
    elif args.no_chime:
        config_overrides['audio'] = {'play_chime': False}

    # Add volume override if provided
    if args.volume is not None:
        if 0.0 <= args.volume <= 1.0:
            if 'audio' not in config_overrides:
                config_overrides['audio'] = {}
            config_overrides['audio']['volume'] = args.volume
        else:
            print("Error: Volume must be between 0.0 and 1.0", file=sys.stderr)
            return 1

    try:
        clock = SpeakingClock(config_path=args.config, config_overrides=config_overrides)
        success = clock.speak_time(custom_time=args.time)
        return 0 if success else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
