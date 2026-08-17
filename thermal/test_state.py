from thermal.controller import ThermalController


thermal = ThermalController()

temperatures = [
    50,
    64,
    65,
    68,
    74,
    75,
    80,
    73,
    70,
    69,
    61,
    59,
]


for temperature in temperatures:
    state, changed = thermal.update(temperature)

    print(
        f"Temperature: {temperature:5.1f}°C"
        f"  →  State: {state:6s}"
        f"  →  Changed: {changed}"
    )
