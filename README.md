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

## Installation

This app is regular Python package and is also hosted
on [PyPi](https://pypi.org/project/speaking-clock/) so
you can install it as usual. But because this one is supposed to rather act as the application, I
strongly recommend to use [pipx](https://pipx.pypa.io/) to install this tool in isolated
environment be it on Linux, Windows or MacOS machines. Once you got `pipx` up
and running, install the package:

```bash
$ pipx install speaking-clock
```

Of course, you can also use plain `pip` to do that:

```bash
$ pip install speaking-clock
```

But that might be a problem as some distributions no longer allow system-wide installations,
therefore use of `pipx` is strongly recommended as the all-in-one solution.

Once installed `speaking-clock` executable (and it's alias `speak-time`) should be available in
your system ready to be used. Please use `--help` to see all available options.

## Usage

### As a command-line tool

Once installed, you can use the command-line interface:

```
speak-time
```

You can specify a custom config file:

```
speak-time --config /path/to/your/config.yml
```

### Configuration

The speaking-clock looks for configuration in the following places:

1. Command-line specified config (if provided)
1. User config file at `~/.config/speaking-clock/config.yml`
1. Default configuration built into the package

You can create a config file at `~/.config/speaking-clock/config.yml` with the following structure:

```yaml
language:
  code: "pl"              # Language code matching a file in 'languages/' directory
  use_24h_clock: true     # Use 24-hour (true) or 12-hour (false) format

elevenlabs:
  api_key: "your-api-key-here"  # Your ElevenLabs API key
  voice_id: "voice-id-here"     # ElevenLabs voice ID
  model_id: "eleven_multilingual_v2"  # TTS model to use

audio:
  play_chime: true        # Play a chime before speaking the time
  chime_file: "clock-chime.mp3"  # Path to the chime audio file
  overlay_speech: true    # Overlay speech over the chime sound
  speech_offset_ms: 1000  # Milliseconds to wait before starting speech

cache:
  directory: ".cache"     # Directory for caching audio files
```

You can also set your ElevenLabs API key as an environment variable:

```
export ELEVENLABS_API_KEY="your-api-key-here"
```

## Language Support

The application supports multiple languages through YAML language definition files. These files are stored in the `languages/` directory with filenames matching their language code (e.g., `pl.yml` for Polish).

To add support for a new language:

1. Create a new YAML file in the `languages/` directory (e.g., `en.yml` for English)
1. Define the language elements following the structure in the existing language files
1. Update the `language.code` value in `config.yml` to match your new language file

Example language file structure:

```yaml
days_of_week:
  - poniedziałek  # Monday
  - wtorek        # Tuesday
  # ...

hours:
  0: dwudziesta czwarta
  1: pierwsza
  # ...

special_minutes:
  0: ""
  15: piętnaście
  # ...

special_times:
  midnight: północ, nastał {day_name}
```

## Cache Files

Audio files are automatically cached in the `.cache` directory using the following naming convention:

```
LANG-VOICE-HH-MM.mp3
```

For example:

```
pl-voice_id-13-05.mp3  # Polish, voice_id, 13:05
```

This caching system ensures that each unique time announcement is only generated once, reducing API calls to ElevenLabs and improving response time for frequently requested times.

# Audio Support for Cron Jobs in KDE 5

## Problem

When running Python applications from cron jobs in KDE 5, audio playback doesn't work automatically. This is because cron jobs run in a separate environment without access to your desktop session's audio system.

## Solution

Configure the cron job with specific environment variables to access your KDE desktop session's audio services.

### Required Environment Variables

For audio playback in KDE 5, your cron job needs these key environment variables:

- `DISPLAY`: Points to your X server display
- `DBUS_SESSION_BUS_ADDRESS`: Connects to your D-Bus session
- `XDG_RUNTIME_DIR`: Required for PulseAudio/PipeWire access

### Setting Up the Cron Job

Edit your crontab:

```bash
crontab -e
```

Add your job using this template:

```bash
# Run every hour at minute 0
0 * * * * DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME plasma-session)/environ | cut -d= -f2-) XDG_RUNTIME_DIR=/run/user/$(id -u) python /path/to/your/script.py
```

### Testing Your Configuration

To test without waiting for the scheduled time:

```bash
# Test the exact command that cron will run
DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME plasma-session)/environ | cut -d= -f2-) XDG_RUNTIME_DIR=/run/user/$(id -u) python /path/to/your/script.py
```

## Troubleshooting

### Common Issues and Solutions

1. **No audio despite correct configuration**:

   - Ensure PulseAudio is running: `pulseaudio --check`
   - Try adding `PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native` to your environment variables

1. **D-Bus address not found**:

   - If plasma-session isn't found, try: `pgrep -u $LOGNAME plasmashell` instead

1. **Permission issues**:

   - Check audio group membership: `groups | grep audio`
   - Add yourself if needed: `sudo usermod -a -G audio $USER`

1. **Application-specific audio servers**:

   - For PipeWire: Add `PIPEWIRE_RUNTIME_DIR=${XDG_RUNTIME_DIR}/pipewire-0`

## Limitations

This solution only works when:

- You are logged into your KDE session
- You are using the same user account for both KDE and the cron job
