from thermal.controller import TemperatureReader, ThermalController
from asus_led.controller import AsusLED


reader = TemperatureReader()
thermal = ThermalController()
led = AsusLED()

temperatures = reader.get_temperatures()
maximum = reader.get_max_temperature(temperatures)

state, changed = thermal.update(maximum)

print(f"CPU:   {temperatures['cpu']:.1f}°C")
print(f"GPU:   {temperatures['gpu']:.1f}°C")
print(f"MAX:   {maximum:.1f}°C")
print(f"STATE: {state}")
print(f"CHANGED: {changed}")

if changed:
    led.set_named_color(state)
    print("LED updated.")
else:
    print("LED update not required.")
