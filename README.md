# rog_ctl

A small Linux controller for the ASUS ROG Strix G513QE. It monitors the CPU
and NVIDIA GPU temperatures and uses `asusctl` to show the hottest thermal
state on the keyboard LEDs:

| State | Entry threshold | Exit threshold | LED color |
| --- | ---: | ---: | --- |
| Green | below 65°C | below 60°C from yellow | `00ff00` |
| Yellow | 65°C | below 60°C | `ffff00` |
| Red | 75°C | below 70°C | `ff0000` |

The different entry and exit thresholds provide hysteresis, preventing the
LED color from flickering when the temperature is close to a boundary. The
controller polls once per second by default and only updates the LEDs when
the thermal state changes.

## Requirements

- Linux with readable `/sys/class/hwmon`
- An AMD CPU exposing the `k10temp` hwmon device
- An NVIDIA GPU with `nvidia-smi` available on `PATH`
- `asusctl` installed and configured to control the keyboard LEDs
- Python 3.9 or newer

This repository contains the Python controller only. The `asusctl` command is
an external dependency; it is not installed by this project.

## Run

From the repository root:

```bash
python3 main.py
```

Stop it with `SIGTERM`:

```bash
kill -TERM <pid>
```

On startup, the controller prints the configured thresholds. It continues
polling after an individual sensor or LED operation fails and reports the
error to standard output.

## Configuration

Edit [config.py](config.py) to change the polling interval, thermal
thresholds, or RGB values:

```python
POLL_INTERVAL = 1.0
YELLOW_ENTER = 65.0
YELLOW_EXIT = 60.0
RED_ENTER = 75.0
RED_EXIT = 70.0
```

The color names in `COLORS` must match the thermal states used by
`ThermalController`.

## Checks and diagnostics

The repository does not currently use a test runner. The state-transition
script is hardware-independent:

```bash
python3 -m thermal.test_state
```

These scripts require the listed hardware and system commands:

```bash
python3 thermal/test_led.py   # Read sensors and update the LED if needed
python3 asus_led/test.py      # Read brightness and set a red static effect
```

## Project layout

- `main.py` - polling loop and signal handling
- `thermal/controller.py` - CPU/GPU temperature readers and hysteresis state machine
- `asus_led/controller.py` - `asusctl` brightness and Aura effect integration
- `config.py` - polling, threshold, and color configuration
- `thermal/test_state.py` - hardware-independent state-transition diagnostic
- `thermal/test_led.py`, `asus_led/test.py` - hardware-facing diagnostics

## Limitations

- Temperature discovery is currently specific to `k10temp` and NVIDIA's
	`nvidia-smi` output.
- The process is intended to run in the foreground; no service unit is
	provided in the tracked project files.
- Sensor and command failures are logged, but there is no retry backoff or
	persistent logging configuration.
