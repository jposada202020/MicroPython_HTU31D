# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`htu31d`
================================================================================

MicroPython library for TE HTU31D temperature and humidity sensors


* Author(s): ladyada, Jose D. Montoya


"""

import time
import struct
from micropython import const

try:
    from typing import Tuple, Any, Literal
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_HTU31D.git"

_READSERIAL = const(0x0A)  # Read Out of Serial Register
_SOFTRESET = const(0x1E)  # Soft Reset
_HEATERON = const(0x04)  # Enable heater
_HEATEROFF = const(0x02)  # Disable heater
_CONVERSION = const(0x40)  # Start a conversion
_READTEMPHUM = const(0x00)  # Read the conversion values

_HUMIDITY_RES = ("0.020%", "0.014%", "0.010%", "0.007%")
_TEMP_RES = ("0.040", "0.025", "0.016", "0.012")


class HTU31D:
    """Driver for the HTU31D Sensor connected over I2C.

    :param ~machine.I2C i2c: The I2C bus the HTU31D is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x40`


    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`HTU31D` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        from machine import Pin, I2C
        from micropython_htu31d import htu31d

    Once this is done you can define your `machine.I2C` object and define your sensor object

    .. code-block:: python

        i2c = I2C(1, sda=Pin(2), scl=Pin(3))
        htu31d = htu31d.HTU31D(i2c)

    Now you have access to the :attr:`temperature` and :attr:`relative_humidity`
    attributes

    .. code-block:: python

        temperature = htu.temperature
        relative_humidity = htu.relative_humidity

    """

    def __init__(self, i2c, address: int = 0x40) -> None:
        self._i2c = i2c
        self._address = address
        self._buffer = bytearray(4)
        self._data = bytearray(6)
        self._conversion_command = _CONVERSION
        self.reset()
        self._heater = False

    @property
    def serial_number(self) -> tuple[Any, ...]:
        """The unique 32-bit serial number"""

        self._i2c.writeto(self._address, bytes([_READSERIAL]), False)
        self._i2c.readfrom_into(self._address, self._buffer)
        ser = struct.unpack(">I", self._buffer)

        return ser

    def reset(self) -> None:
        """Perform a soft reset of the sensor, resetting all settings to their power-on defaults"""
        self._conversion_command = _CONVERSION
        self._i2c.writeto(self._address, bytes([_SOFTRESET]), False)
        time.sleep(0.015)

    @property
    def heater(self) -> bool:
        """The current sensor heater mode"""
        return self._heater

    @heater.setter
    def heater(self, new_mode: bool) -> None:
        # check it is a boolean
        if not isinstance(new_mode, bool):
            raise AttributeError("Heater mode must be boolean")
        # cache the mode
        self._heater = new_mode
        # decide the command!
        if new_mode:
            payload = bytes([_HEATERON])
        else:
            payload = bytes([_HEATEROFF])

        self._i2c.writeto(self._address, payload, False)

    @property
    def relative_humidity(self) -> float:
        """The current relative humidity in % rH"""
        return self.measurements[1]

    @property
    def temperature(self) -> float:
        """The current temperature in degrees Celsius"""
        return self.measurements[0]

    @property
    def measurements(self) -> Tuple[float, float]:
        """both `temperature` and `relative_humidity`, read simultaneously"""

        self._i2c.writeto(self._address, bytes([self._conversion_command]), False)
        time.sleep(0.03)
        self._i2c.writeto(self._address, bytes([_READTEMPHUM]), False)
        self._i2c.readfrom_into(self._address, self._data)

        # separate the read data
        temperature, temp_crc, humidity, humidity_crc = struct.unpack_from(
            ">HBHB", self._data
        )

        # check CRC of bytes
        if temp_crc != self._crc(temperature) or humidity_crc != self._crc(humidity):
            raise RuntimeError("Invalid CRC calculated")

        temperature = -40.0 + 165.0 * temperature / 65535.0

        # repeat above steps for humidity data
        humidity = 100 * humidity / 65535.0
        humidity = max(min(humidity, 100), 0)

        return temperature, humidity

    @staticmethod
    def _crc(value) -> int:
        polynom = 0x988000  # x^8 + x^5 + x^4 + 1
        msb = 0x800000
        mask = 0xFF8000
        result = value << 8  # Pad with zeros as specified in spec

        while msb != 0x80:
            # Check if msb of current value is 1 and apply XOR mask
            if result & msb:
                result = ((result ^ polynom) & mask) | (result & ~mask)
            # Shift by one
            msb >>= 1
            mask >>= 1
            polynom >>= 1

        return result

    @property
    def humidity_resolution(self) -> Literal["0.020%", "0.014%", "0.010%", "0.007%"]:
        """The current relative humidity resolution in % rH.

        Possibles values:

            * "0.020%"
            * "0.014%"
            * "0.010%"
            * "0.007%"

        """

        return _HUMIDITY_RES[self._conversion_command >> 3 & 3]

    @humidity_resolution.setter
    def humidity_resolution(
        self, value: Literal["0.020%", "0.014%", "0.010%", "0.007%"]
    ) -> None:
        if value not in _HUMIDITY_RES:
            raise ValueError(f"Humidity resolution must be one of: {_HUMIDITY_RES}")
        register = self._conversion_command & 0xE7
        hum_res = _HUMIDITY_RES.index(value)
        self._conversion_command = register | hum_res << 3

    @property
    def temp_resolution(self) -> Literal["0.040", "0.025", "0.016", "0.012"]:
        """The current temperature resolution in Celsius.

        Possibles values:

            * "0.040"
            * "0.025"
            * "0.016"
            * "0.012"

        """

        return _TEMP_RES[self._conversion_command >> 1 & 3]

    @temp_resolution.setter
    def temp_resolution(
        self, value: Literal["0.040", "0.025", "0.016", "0.012"]
    ) -> None:
        if value not in _TEMP_RES:
            raise ValueError(f"Temperature resolution must be one of: {_TEMP_RES}")
        register = self._conversion_command & 0xF9
        temp_res = _TEMP_RES.index(value)
        self._conversion_command = register | temp_res << 1
