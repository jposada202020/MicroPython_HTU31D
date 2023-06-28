# SPDX-FileCopyrightText: Copyright (c) 2021 Jose David M.
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_htu31d import htu31d

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
htu = htu31d.HTU31D(i2c)

print("Temperature Resolution: ", htu.temp_resolution)
print("Humidity Resolution: ", htu.humidity_resolution)

hum_res = ["0.020%", "0.014%", "0.010%", "0.007%"]
temp_res = ["0.040", "0.025", "0.016", "0.012"]

while True:
    for humidity_resolution in hum_res:
        htu.humidity_resolution = humidity_resolution
        print(f"Current Humidity Resolution: {humidity_resolution}")
        for _ in range(2):
            print(f"Humidity: {htu.relative_humidity:.2f}")
            print(f"Temperature: {htu.temperature:.2f}")
            print("")
            time.sleep(0.5)
    for temperature_resolution in temp_res:
        htu.temp_resolution = temperature_resolution
        print(f"Current Temperature Resolution: {temperature_resolution}")
        for _ in range(2):
            print(f"Humidity: {htu.relative_humidity:.2f}")
            print(f"Temperature: {htu.temperature:.2f}")
            print("")
            time.sleep(0.5)

