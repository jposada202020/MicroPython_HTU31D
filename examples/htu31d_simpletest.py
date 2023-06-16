# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_htu31d import htu31d

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
htu = htu31d.HTU31D(i2c)

print("Found HTU31D with serial number", hex(htu.serial_number))

htu.heater = True
print("Heater is on?", htu.heater)
htu.heater = False
print("Heater is on?", htu.heater)

print(htu.measurements)

while True:
    temperature, relative_humidity = htu.measurements
    print("Temperature: %0.1f C" % temperature)
    print("Humidity: %0.1f %%" % relative_humidity)
    print("")
    time.sleep(1)
