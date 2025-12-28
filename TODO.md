- Refactor config and move `chime` to separate section
- Add more chime control (full hours, hal hours, quadrants)
- Add option to define chime config per any time (with "HH:MM" being key), like audio, enabled etc
- add cascade settings handing. i.e. we Look for settings for "HH:MM", if not there we look for
  ":MM", then we look for "HH:" then we look for "\*"
