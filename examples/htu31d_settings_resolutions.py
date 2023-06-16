# SPDX-FileCopyrightText: Copyright (c) 2021 Jose David M.
#
# SPDX-License-Identifier: MIT

from machine import Pin, I2C
from micropython_htu31d import htu31d

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
htu = htu31d.HTU31D(i2c)

print("Temperature Resolution: ", htu.temp_resolution)
print("Humidity Resolution: ", htu.humidity_resolution)

# Setting the temperature resolution.
# Possible values are "0.040", "0.025", "0.016" and "0.012"
htu.temp_resolution = "0.016"

# Setting the Relative Humidity resolution.
# Possible values are "0.020%", "0.014%", "0.010%" and "0.007%"
htu.humidity_resolution = "0.007%"

# Printing the New Values
print("Temperature Resolution: ", htu.temp_resolution)
print("Humidity Resolution: ", htu.humidity_resolution)
