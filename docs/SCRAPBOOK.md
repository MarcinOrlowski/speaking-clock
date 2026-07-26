### Option 1: Install from source

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/speaking-clock.git
   cd speaking-clock
   ```

1. Install the package:

   ```
   pip install -e .
   ```

### Option 2: Install from development package

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/speaking-clock.git
   cd speaking-clock
   ```

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```


### Installation via `pip`

...
Of course, you can also use plain `pip` to do that:

```bash
$ pip install speaking-clock
```

But that might be a problem as some distributions no longer allow system-wide installations,
therefore use of `pipx` is strongly recommended as the all-in-one solution.

Once installed `speaking-clock` executable (and it's alias `speak-time`) should be available in
your system ready to be used. Please use `--help` to see all available options.


## Usage

### As a Python module

```python
from speaking_clock import speak_time

# Speak the current time using default config
speak_time()

# Or use the full API
from speaking_clock import SpeakingClock

# Initialize with default config or specify a path
clock = SpeakingClock()  # or SpeakingClock('/path/to/config.yml')
clock.speak_time()
```
