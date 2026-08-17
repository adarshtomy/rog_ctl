import subprocess

from config import COLORS

BRIGHTNESS_PREFIX = "Current keyboard led brightness: "


class AsusLED:
    """ASUS keyboard RGB controller using asusctl."""
    def set_named_color(self, name):
        """Set one of the predefined LED colors."""

        name = name.lower()

        if name not in COLORS:
            raise ValueError(
                f"Unknown color '{name}'. "
                f"Available colors: {', '.join(COLORS)}"
            )

        self.set_color(COLORS[name])
        
    def get_brightness(self):
        result = subprocess.run(
            ["asusctl", "leds", "get"],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout.strip()

        if not output.startswith(BRIGHTNESS_PREFIX):
            raise RuntimeError(
                f"Unexpected asusctl brightness output: {output}"
            )

        return output.removeprefix(BRIGHTNESS_PREFIX).lower()

    def set_brightness(self, brightness):
        valid = {"off", "low", "med", "high"}

        if brightness not in valid:
            raise ValueError(
                f"Invalid brightness '{brightness}'. "
                f"Expected one of: {', '.join(sorted(valid))}"
            )

        subprocess.run(
            ["asusctl", "leds", "set", brightness],
            check=True,
        )

    def set_color(self, color):
        """
        Set static RGB color while preserving the current
        keyboard brightness.
        """

        brightness = self.get_brightness()

        subprocess.run(
            ["asusctl", "aura", "effect", "static", "-c", color],
            check=True,
        )

        self.set_brightness(brightness)
