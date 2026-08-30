# rog_ctl

Linux thermal controller for the **ASUS ROG Strix G513QE**.

`rog_ctl` monitors CPU and NVIDIA GPU temperatures, determines the thermal state using hysteresis, and controls the keyboard RGB through `asusctl`.

| State  |  Enter |   Exit | LED      |
| ------ | -----: | -----: | -------- |
| Green  | < 65°C |      — | `00ff00` |
| Yellow | ≥ 65°C | < 60°C | `ffff00` |
| Red    | ≥ 75°C | < 70°C | `ff0000` |

The controller polls every second by default and only changes the LED when the thermal state changes.

## Architecture

```text
Sensors
  ├── CPU → /sys/class/hwmon (k10temp)
  └── GPU → nvidia-smi
          ↓
   ThermalController
   └── hysteresis state machine
          ↓
     LED Controller
          ↓
       asusctl
          ↓
     ROG keyboard
```

```text
rog_ctl/
├── main.py
├── config.py
├── thermal/
│   ├── controller.py
│   ├── test_state.py
│   └── test_led.py
├── asus_led/
│   ├── controller.py
│   └── test.py
└── systemd/
    └── rog-led.service
```

## Requirements

* Linux
* AMD CPU with `k10temp`
* NVIDIA GPU with `nvidia-smi`
* `asusctl`
* Python 3.9+

`asusctl` is an external system dependency.

## Run manually

From the project directory:

```bash
python3 main.py
```

Stop:

```bash
kill -TERM <PID>
```

## Run with systemd

Install the service unit:

```bash
sudo cp systemd/rog-led.service /etc/systemd/system/
sudo systemctl daemon-reload
```

Start:

```bash
sudo systemctl start rog-led
```

Enable at boot:

```bash
sudo systemctl enable rog-led
```

Enable and start together:

```bash
sudo systemctl enable --now rog-led
```

## Service control

Check status:

```bash
systemctl status rog-led
```

Start:

```bash
sudo systemctl start rog-led
```

Stop:

```bash
sudo systemctl stop rog-led
```

Restart:

```bash
sudo systemctl restart rog-led
```

Disable automatic startup:

```bash
sudo systemctl disable rog-led
```

Check whether it is enabled:

```bash
systemctl is-enabled rog-led
```

Check whether it is running:

```bash
systemctl is-active rog-led
```

## Logs

Show recent logs:

```bash
journalctl -u rog-led
```

Follow logs live:

```bash
journalctl -u rog-led -f
```

Show logs from the current boot:

```bash
journalctl -u rog-led -b
```

Show the last 50 lines:

```bash
journalctl -u rog-led -n 50
```

## Configuration

Thermal thresholds, polling interval, and LED colors are defined in:

```text
config.py
```

Example:

```python
POLL_INTERVAL = 1.0
YELLOW_ENTER = 65.0
YELLOW_EXIT = 60.0
RED_ENTER = 75.0
RED_EXIT = 70.0
```

## Diagnostics

Hardware-independent state-machine check:

```bash
python3 -m thermal.test_state
```

Hardware/sensor test:

```bash
python3 thermal/test_led.py
```

ASUS LED test:

```bash
python3 asus_led/test.py
```

## Design

The controller separates **thermal sensing/state logic** from **hardware-specific LED control**. Hysteresis prevents rapid state switching near temperature boundaries, while failures in an individual sensor or LED operation do not terminate the main polling loop.

