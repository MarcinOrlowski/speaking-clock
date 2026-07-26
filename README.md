![Speaking Clock](img/logo.webp)

# Speaking Clock

A small utility that speaks (usually current) time in specified language. Uses ElevenLabs API to
generate the speech. Supports caching and reusing audio files so free ElevenLabs access is more than
enough. Handy to sit in cron jobs to periodically announce the time.

## Features

- Gets the current time and speaks it in specified language
- Uses ElevenLabs API for high-quality text-to-speech
- Caches generated audio files for quick reuse
- Supports both 12-hour and 24-hour time formats
- Optional audio chime before speaking the time
- Parallel processing - prepares audio while chime is playing
- Overlaid audio playback with configurable timing offset
- Command-line interface driven, perfect for background jobs like cron

## Installation

This app is regular Python package and is also hosted
on [PyPi](https://pypi.org/project/speaking-clock/) so you can install it as usual. But because this
one is supposed to rather act as the application, I strongly recommend to
use [pipx](https://pipx.pypa.io/) to install this tool in isolated environment be it on Linux,
Windows or MacOS machines. Once you got `pipx` up and running, install the package:

```bash
$ pipx install speaking-clock
```

## Usage

Once installed, you can use the command-line interface:

```bash
$ speak-time
```

### Configuration

The speaking-clock looks for configuration in the following places:

1. Command-line specified config (if provided)
1. User config file at `~/.config/speaking-clock/config.yml`
1. Default configuration built into the package

You can create a config file at `~/.config/speaking-clock/config.yml` with the following structure:

```yaml
language:
  code: "pl"
  use_24h_clock: true

elevenlabs:
  # To get your ElevenLabs API key, loging to your account and go to
  #   https://elevenlabs.io/app/developers/api-keys
  #
  # Then create new key. Make sure the following endpoint access is granted:
  # - Text so Speed: Acesss
  # - Voices: Read
  #
  api_key: "<YOUR API KEY>"

  # Voice name or ID from your ElevenLabs account. Give a list to set up fallbacks
  # if needed (see docs for details):
  # voice_id:
  #   - "<PREFERRED VOICE>"
  #   - "<FALLBACK VOICE>"
  #
  voice_id: "<VOICE NAME OR ID>"
  model_id: "eleven_multilingual_v2"

audio:
  overlay_speech: true           # Set to true to overlay speech over the chime.
                                 # If false, speech will start after the chime ends
  speech_offset_ms: 1000         # Milliseconds to wait before starting speech after chime plays
  volume: 1.0                    # Volume level from 0.0 (muted) to 1.0 (full)

chime:
  enabled: true  # Set to true to play a chime before speaking the time
  audio_file: "clock-chime.mp3"  # Path to the chime audio file

cache:
  enabled: true                  # Set to false to always generate speech instead of reusing cache

  # Defaults to "$XDG_CACHE_HOME/speaking-clock/", or "~/.cache/speaking-clock/"
  # directory: "~/.cache/speaking-clock"

```

#### Voice fallbacks

`voice_id` also takes a list, which turns each entry into a fallback for the one before it:

```yaml
elevenlabs:
  voice_id:
    - "Bratanek"
    - "George"
```

Voices are tried in order, and each one is tried in full before the next: its cached
announcements first, then the API. So a voice that has become unavailable - one that moved
behind a paid tier, say - keeps playing back whatever was cached while it still worked, and
announcements it never cached come from the next voice in the list. The run fails only when
every voice misses both its cache and the API.

Whatever the skipped voices had to say - an API error, an unknown voice name - stays quiet as
long as a later voice delivers, and is reported only when the whole list comes up empty.

You can also set your ElevenLabs API key as an environment variable:

```bash
export ELEVENLABS_API_KEY="your-api-key-here"
```

### Using custom configuration file

You can specify a custom config file:

```bash
speak-time --config /path/to/your/config.yml
```

## Language Support

The application supports multiple languages through YAML language definition files. These files are
stored in the `languages/` directory with filenames matching their language code (e.g., `pl.yml`
for Polish).

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

Audio files are automatically cached in `$XDG_CACHE_HOME/speaking-clock`, falling back to
`~/.cache/speaking-clock` when `XDG_CACHE_HOME` is unset (or holds a relative path). Set
`cache.directory` in the config file, or pass `--cache <DIR>`, to use another location.

Cached files follow the naming convention:

```ascii
LANG-VOICE-HH-MM.mp3
```

For example:

```ascii
pl-voice_id-13-05.mp3  # Polish, voice_id, 13:05
```

This caching system ensures that each unique time announcement is only generated once, reducing API
calls to ElevenLabs and improving response time for frequently requested times.

Pass `--no-cache` to bypass the cache for a single run - the announcement is then generated fresh
and is not written to disk:

```bash
speak-time --no-cache
```

Set `cache.enabled: false` in the config file to disable caching permanently. Note that with the
cache off, a voice that is no longer available from the API can no longer fall back to what it
cached earlier, so a [voice chain](#voice-fallbacks) loses that safety net.

# Audio Support for Cron Jobs in KDE 5

## Problem

When running Python applications from cron jobs in KDE 5, audio playback doesn't work automatically.
This is because cron jobs run in a separate environment without access to your desktop session's
audio system.

## Solution

Configure the cron job with specific environment variables to access your KDE desktop session's
audio services.

### Required Environment Variables

For audio playback in KDE 5, your cron job needs these key environment variables:

- `DISPLAY`: Points to your X server display
- `DBUS_SESSION_BUS_ADDRESS`: Connects to your D-Bus session
- `XDG_RUNTIME_DIR`: Required for PulseAudio/PipeWire access

### Setting Up the Cron Job

Edit your crontab and add your job using this template (it's assumed app is
installed via `pipx` so its binary sits in `~/.local/bin/` folder):

<!-- markdownlint-disable MD013 -- a crontab entry must be a single line; cron has no line continuation -->

```bash
# Run every hour at minute 0
0 * * * * DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -u $LOGNAME plasma-session)/environ | cut -d= -f2-) XDG_RUNTIME_DIR=/run/user/$(id -u) .local/bin/speak-time
```

<!-- markdownlint-enable MD013 -->

### Testing Your Configuration

To test without waiting for the scheduled time:

```bash
# Test the exact command that cron will run
DISPLAY=:0 \
  DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS \
    /proc/$(pgrep -u $LOGNAME plasma-session)/environ | cut -d= -f2-) \
  XDG_RUNTIME_DIR=/run/user/$(id -u) \
  .local/bin/speak-time
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
