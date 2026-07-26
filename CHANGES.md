# Changes

## v1.2.0 (TBD)

- Updated documentation.

## v1.1.0 (2026-07-26)

- Fixed speech generation failing against ElevenLabs SDK 2.x.
- Fixed audio playback crashing with `'module' object is not callable` on ElevenLabs SDK 2.x.
- ElevenLabs API errors now report just the message instead of dumping every HTTP header.
- The `voice_id` now accepts a voice name along voice ID.
- The `voice_id` accepts multiple voices and use them as fallback if previous is not available.
- Fixed `--chime` and `--no-chime` having no effect.
- Fixed volume control being a silent no-op on Python 3.13+
- Fixed `pydub` and `numpy` missing from the installed package's dependencies.
- Consolidated packaging metadata into `pyproject.toml`
- Added `--no-cache` and `cache.enabled` to skip both reading and writing cached announcements.
- Default audio cache location now honours `$XDG_CACHE_HOME`.
- Cache directory is now created on first write instead of on every run.
- Fixed `--cache` being parsed but ignored.
- Raised the declared minimum Python from 3.7 to 3.8.

## v1.0.0 (2025-12-28)

- Initial public release
