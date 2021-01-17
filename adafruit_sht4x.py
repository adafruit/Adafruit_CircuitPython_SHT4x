# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 ladyada for Adafruit
#
# SPDX-License-Identifier: MIT
"""
`adafruit_sht4x`
================================================================================

Python library for Sensirion SHT4x temperature and humidity sensors

* Author(s): ladyada

Implementation Notes
--------------------

**Hardware:**

Python library for Sensirion SHT4x temperature and humidity sensors

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

import time
import adafruit_bus_device.i2c_device as i2c_device
from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_SHT4x.git"


_SHT4X_DEFAULT_ADDR = const(0x44)  # SHT4X I2C Address
_SHT4X_READSERIAL = const(0x89) # Read Out of Serial Register
_SHT4X_SOFTRESET = const(0x94)  # Soft Reset

class SHT4x:
    """
    A driver for the SHT4x temperature and humidity sensor.

    :param ~busio.I2C i2c_bus: The `busio.I2C` object to use. This is the only required parameter.

    """

    def __init__(self, i2c_bus):
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, _SHT4X_DEFAULT_ADDR)
        self._buffer = bytearray(6)
        self.reset()

    def _write_command(self, command):
        self._buffer[0] = command >> 8
        self._buffer[1] = command & 0xFF

        with self.i2c_device as i2c:
            i2c.write(self._buffer, start=0, end=2)

    @property
    def serial_number(self):
        self._buffer[0] = _SHT4X_READSERIAL
        with self.i2c_device as i2c:
            i2c.write(self._buffer, end=1)
            time.sleep(0.01)
            i2c.readinto(self._buffer)

        ser1 = self._buffer[0:2]
        ser1_crc = self._buffer[2]
        ser2 = self._buffer[3:5]
        ser2_crc = self._buffer[5]

        # check CRC of bytes
        if ser1_crc != self._crc8(ser1) or ser2_crc != self._crc8(ser2):
            raise RuntimeError("Invalid CRC calculated")

        serial = (ser1[0] << 24) + (ser1[1] << 16) + (ser2[0] << 8) + ser2[1]
        return serial

    def reset(self):
        """Perform a soft reset of the sensor, resetting all settings to their power-on defaults"""
        self._buffer[0] = _SHT4X_SOFTRESET
        with self.i2c_device as i2c:
            i2c.write(self._buffer, end=1)
        
        time.sleep(0.001)

    @property
    def sleeping(self):
        """Determines the sleep state of the sensor"""
        return self._cached_sleep

    @sleeping.setter
    def sleeping(self, sleep_enabled):
        if sleep_enabled:
            self._write_command(_SHTC3_SLEEP)
        else:
            self._write_command(_SHTC3_WAKEUP)
        time.sleep(0.001)
        self._cached_sleep = sleep_enabled

    # lowPowerMode(bool readmode) { _lpMode = readmode

    @property
    def low_power(self):
        """Enables the less accurate low power mode, trading accuracy for power consumption"""
        return self._low_power

    @low_power.setter
    def low_power(self, low_power_enabled):
        self._low_power = low_power_enabled

    @property
    def relative_humidity(self):
        """The current relative humidity in % rH"""
        return self.measurements[1]

    @property
    def temperature(self):
        """The current temperature in degrees celcius"""
        return self.measurements[0]

    @property
    def measurements(self):
        """both `temperature` and `relative_humidity`, read simultaneously"""

        self.sleeping = False
        temperature = None
        humidity = None
        # send correct command for the current power state
        if self.low_power:
            self._write_command(_SHTC3_LOWPOW_MEAS_TFIRST)
            time.sleep(0.001)
        else:
            self._write_command(_SHTC3_NORMAL_MEAS_TFIRST)
            time.sleep(0.013)

        # self._buffer = bytearray(6)
        # read the measured data into our buffer
        with self.i2c_device as i2c:
            i2c.readinto(self._buffer)

        # separate the read data
        temp_data = self._buffer[0:2]
        temp_crc = self._buffer[2]
        humidity_data = self._buffer[3:5]
        humidity_crc = self._buffer[5]

        # check CRC of bytes
        if temp_crc != self._crc8(temp_data) or humidity_crc != self._crc8(
            humidity_data
        ):
            return (temperature, humidity)

        # decode data into human values:
        # convert bytes into 16-bit signed integer
        # convert the LSB value to a human value according to the datasheet
        raw_temp = unpack_from(">H", temp_data)[0]
        raw_temp = ((4375 * raw_temp) >> 14) - 4500
        temperature = raw_temp / 100.0

        # repeat above steps for humidity data
        raw_humidity = unpack_from(">H", humidity_data)[0]
        raw_humidity = (625 * raw_humidity) >> 12
        humidity = raw_humidity / 100.0

        self.sleeping = True
        return (temperature, humidity)

    ## CRC-8 formula from page 14 of SHTC3 datasheet
    # https://media.digikey.com/pdf/Data%20Sheets/Sensirion%20PDFs/HT_DS_SHTC3_D1.pdf
    # Test data [0xBE, 0xEF] should yield 0x92

    @staticmethod
    def _crc8(buffer):
        crc = 0xFF
        for byte in buffer:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1
        return crc & 0xFF  # return the bottom 8 bits
