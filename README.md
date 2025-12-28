```
 ▄▀▀▄                █     ▀                ▄▀▀▄ ▀█            █
 ▀▄▄  █▀▀▄ ▄▀▀▄ ▄▀▀▄ █ ▄▀ ▀█  █▀▀▄ ▄▀▀█     █     █  ▄▀▀▄ ▄▀▀▄ █ ▄▀
    █ █  █ █▀▀   ▄▄█ █▀▄   █  █  █ █  █     █     █  █  █ █    █▀▄
 ▀▄▄▀ █▄▄▀ ▀▄▄▀ ▀▄▄▀ █  █ ▄█▄ █  █ ▀▄▄█     ▀▄▄▀ ▄█▄ ▀▄▄▀ ▀▄▄▀ █  █
      █                             ▄▄▀

 @project   Speaking Clock - time announcer using ElevenLabs TTS API
 @author    Marcin Orlowski <mail (#) marcinOrlowski (.) com>
 @copyright 2025 Marcin Orlowski
 @license   https://www.opensource.org/licenses/mit-license.php MIT
 @link      https://github.com/MarcinOrlowski/speaking-clock
```

# Speaking Clock

A small utility that speaks (usually current) time in specified language. Uses ElevenLabs API 
to generate the speech. Supports caching and reusing audio files so free ElevenLabs
access is more than enough. Handy to sit in cron jobs to periodically announce the time.

## Features

- Gets the current time and speaks it in specified language
- Converts numbers to their Polish word representation (e.g., "13:05" → "trzynasta pięć")
- Uses ElevenLabs API for high-quality text-to-speech
- Caches generated audio files for quick reuse
- Supports both 12-hour and 24-hour time formats
- Optional audio chime before speaking the time
- Parallel processing - prepares audio while chime is playing
- Overlaid audio playback with configurable timing offset
- Command-line interface driven, perfect for background jobs like cron

