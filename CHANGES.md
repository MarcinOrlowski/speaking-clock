# Changes

## v1.1.0 (TBD)

* Fixed speech generation failing against ElevenLabs SDK 2.x, which removed `client.generate()`.
* Fixed audio playback crashing with `'module' object is not callable` on ElevenLabs SDK 2.x.
* ElevenLabs API errors now report just the message instead of dumping every HTTP header.
* `voice_id` now accepts a voice name, so `"George"` resolves without needing its full
  `"George - Warm, Captivating Storyteller"` name or its ID.
* Fixed `--chime` and `--no-chime` having no effect.
* Fixed volume control being a silent no-op on Python 3.13+
* Fixed `pydub` and `numpy` missing from the installed package's dependencies.
* Consolidated packaging metadata into `pyproject.toml`
* Raised the declared minimum Python from 3.7 to 3.8.

## v1.0.0 (2025-12-28)

* Initial public release
