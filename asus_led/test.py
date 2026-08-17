from asus_led.controller import AsusLED


led = AsusLED()

print("Current brightness:", led.get_brightness())

led.set_color("ff0000")

print("Final brightness:", led.get_brightness())
