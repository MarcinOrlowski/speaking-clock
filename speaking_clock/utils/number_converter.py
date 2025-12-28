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

Multilingual number and time conversion utilities
"""
import datetime
import yaml
from pathlib import Path
from num2words import num2words


def load_language_data(language_code):
    """
    Load language data from YAML file

    Args:
        language_code: Language code (e.g., 'pl' for Polish)

    Returns:
        Dictionary with language data or None if file not found
    """
    # Look in different locations for language files
    language_paths = [
        # Package languages directory
        Path(__file__).parent.parent / 'languages' / f'{language_code}.yml',
        # Project root languages directory
        Path(__file__).parent.parent.parent / 'languages' / f'{language_code}.yml',
    ]

    for lang_file in language_paths:
        if lang_file.exists():
            with open(lang_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)

    return None


class PolishNumberConverter:
    """Class for converting numbers to Polish words, with special handling for time expressions"""

    def __init__(self, language_code="pl"):
        """Initialize with language data from YAML file"""
        self.language_code = language_code
        self.language_data = load_language_data(language_code)

        # Fall back to English if specified language not found
        if not self.language_data:
            self.language_code = "en"
            self.language_data = load_language_data("en")

            # If still not found, use hardcoded Polish as default
            if not self.language_data:
                self.language_code = "pl"
                # Default hardcoded values (for backwards compatibility)
                self.HOURS_FEMININE = {
                    1: "pierwsza", 2: "druga", 3: "trzecia", 4: "czwarta",
                    5: "piąta", 6: "szósta", 7: "siódma", 8: "ósma",
                    9: "dziewiąta", 10: "dziesiąta", 11: "jedenasta",
                    12: "dwunasta", 13: "trzynasta", 14: "czternasta",
                    15: "piętnasta", 16: "szesnasta", 17: "siedemnasta",
                    18: "osiemnasta", 19: "dziewiętnasta", 20: "dwudziesta",
                    21: "dwudziesta pierwsza", 22: "dwudziesta druga",
                    23: "dwudziesta trzecia", 0: "dwudziesta czwarta"
                }
                return

        # Use data from YAML file
        self.HOURS_FEMININE = self.language_data["hours"]

    def convert_hour(self, hour: int) -> str:
        """Convert hour to Polish feminine form

        Args:
            hour: Hour in 24-hour format (0-23)

        Returns:
            Polish text for the hour
        """
        hour = hour % 24  # Normalize to 0-23 range
        return self.HOURS_FEMININE[hour]

    def convert_minute(self, minute: int) -> str:
        """Convert minute to Polish words

        Args:
            minute: Minute (0-59)

        Returns:
            Polish text for the minute, empty string if 0
        """
        if minute == 0:
            return ""

        # Use special cases from YAML if available, otherwise fall back to hardcoded
        if self.language_data and "special_minutes" in self.language_data:
            special_minutes = self.language_data["special_minutes"]
            if minute in special_minutes:
                return special_minutes[minute]
        else:
            # Hardcoded special cases
            if minute == 15:
                return "piętnaście"
            elif minute == 30:
                return "trzydzieści"
            elif minute == 45:
                return "czterdzieści pięć"

        # Use num2words for other minutes without leading zeros
        return num2words(minute, lang=self.language_code)


class PolishTimeFormatter:
    """Class for formatting time in Polish language"""

    def __init__(self, language_code="pl"):
        """Initialize with language code"""
        self.language_code = language_code
        self.converter = PolishNumberConverter(language_code)
        self.language_data = load_language_data(language_code)

    def format_time(self, hour: int, minute: int) -> str:
        """Format time in Polish language

        Args:
            hour: Hour in 24-hour format (0-23)
            minute: Minute (0-59)

        Returns:
            Formatted time in Polish (e.g., "trzynasta pięć")
        """
        # Special case for midnight
        if hour == 0 and minute == 0:
            # Get current day of week (0-6, Monday is 0)
            current_day = datetime.datetime.now().weekday()

            # Use day names from YAML if available
            if self.language_data and "days_of_week" in self.language_data:
                day_name = self.language_data["days_of_week"][current_day]
            else:
                # Fallback to hardcoded Polish days
                days = [
                    "poniedziałek", "wtorek", "środa", "czwartek",
                    "piątek", "sobota", "niedziela"
                ]
                day_name = days[current_day]

            # Use midnight format from YAML if available
            if self.language_data and "special_times" in self.language_data and "midnight" in self.language_data["special_times"]:
                return self.language_data["special_times"]["midnight"].format(day_name=day_name)
            else:
                # Fallback to hardcoded format
                return f"północ, nastał {day_name}"

        hour_text = self.converter.convert_hour(hour)
        minute_text = self.converter.convert_minute(minute)

        # Return just the hour if it's on the hour
        if not minute_text:
            return hour_text

        # Otherwise combine hour and minutes
        return f"{hour_text} {minute_text}"
