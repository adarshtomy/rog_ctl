import signal
import time

from config import POLL_INTERVAL
from asus_led.controller import AsusLED
from thermal.controller import TemperatureReader, ThermalController


running = True


def handle_signal(signum, frame):
    global running

    if signum == signal.SIGTERM:
        print("Received SIGTERM. Stopping controller.", flush=True)
        running = False


def main():
    global running

    signal.signal(signal.SIGTERM, handle_signal)

    reader = TemperatureReader()
    thermal = ThermalController()
    led = AsusLED()

    print("ROG LED controller started.", flush=True)
    print(
        f"Thresholds: "
        f"Yellow >= {thermal.yellow_enter:.1f}°C | "
        f"Red >= {thermal.red_enter:.1f}°C",
        flush=True,
    )

    try:
        while running:
            try:
                temperatures = reader.get_temperatures()
                maximum = reader.get_max_temperature(temperatures)

                old_state = thermal.state
                state, changed = thermal.update(maximum)

                if changed:
                    try:
                        led.set_named_color(state)

                        if old_state is None:
                            transition = f"INITIAL → {state.upper()}"
                        else:
                            transition = (
                                f"{old_state.upper()} → {state.upper()}"
                            )

                        print(
                            f"{transition} | "
                            f"CPU: {temperatures['cpu']:.1f}°C | "
                            f"GPU: {temperatures['gpu']:.1f}°C | "
                            f"MAX: {maximum:.1f}°C",
                            flush=True,
                        )

                    except Exception as error:
                        print(
                            f"LED error while setting {state}: {error}",
                            flush=True,
                        )

            except Exception as error:
                print(
                    f"Controller error: {error}",
                    flush=True,
                )

            time.sleep(POLL_INTERVAL)

    finally:
        print("ROG LED controller stopped.", flush=True)


if __name__ == "__main__":
    main()
