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
