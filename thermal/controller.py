from pathlib import Path
import subprocess

from config import (
    YELLOW_ENTER,
    YELLOW_EXIT,
    RED_ENTER,
    RED_EXIT,
)


class TemperatureReader:
    """Read CPU and NVIDIA GPU temperatures."""

    HWMON_PATH = Path("/sys/class/hwmon")

    def _find_hwmon(self, name):
        """Find the hwmon directory for a given sensor name."""

        for hwmon in self.HWMON_PATH.glob("hwmon*"):
            name_file = hwmon / "name"

            if name_file.exists() and name_file.read_text().strip() == name:
                return hwmon

        raise RuntimeError(f"Could not find hwmon device: {name}")

    def get_cpu_temperature(self):
        """Return CPU Tctl temperature in °C."""

        hwmon = self._find_hwmon("k10temp")
        temp_file = hwmon / "temp1_input"

        if not temp_file.exists():
            raise RuntimeError(
                f"CPU temperature sensor not found: {temp_file}"
            )

        # Kernel reports temperature in millidegrees Celsius.
        return int(temp_file.read_text().strip()) / 1000.0

    def get_gpu_temperature(self):
        """Return NVIDIA GPU temperature in °C."""

        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return float(result.stdout.strip())

    def get_temperatures(self):
        """Return CPU and GPU temperatures."""

        return {
            "cpu": self.get_cpu_temperature(),
            "gpu": self.get_gpu_temperature(),
        }

    def get_max_temperature(self, temperatures=None):
        """Return the hottest CPU/GPU temperature."""

        if temperatures is None:
            temperatures = self.get_temperatures()

        return max(temperatures.values())


class ThermalController:
    """Convert CPU/GPU temperature into a thermal state."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

    def __init__(
	    self,
	    yellow_enter=YELLOW_ENTER,
	    yellow_exit=YELLOW_EXIT,
	    red_enter=RED_ENTER,
	    red_exit=RED_EXIT,
    ):
        self.yellow_enter = yellow_enter
        self.yellow_exit = yellow_exit
        self.red_enter = red_enter
        self.red_exit = red_exit

        self.state = None

    def update(self, temperature):
        """
        Update thermal state based on temperature.

        Returns:
            tuple[str, bool]:
                Current state and whether the state changed.
        """

        previous_state = self.state

        if self.state is None:
            self.state = self._initial_state(temperature)

        elif self.state == self.GREEN:
            if temperature >= self.red_enter:
                self.state = self.RED
            elif temperature >= self.yellow_enter:
                self.state = self.YELLOW

        elif self.state == self.YELLOW:
            if temperature >= self.red_enter:
                self.state = self.RED
            elif temperature < self.yellow_exit:
                self.state = self.GREEN

        elif self.state == self.RED:
            if temperature < self.red_exit:
                self.state = self.YELLOW

        changed = self.state != previous_state

        return self.state, changed

    def _initial_state(self, temperature):
        """Determine the initial thermal state."""

        if temperature >= self.red_enter:
            return self.RED

        if temperature >= self.yellow_enter:
            return self.YELLOW

        return self.GREEN
