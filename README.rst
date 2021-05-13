Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-sht4x/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/sht4x/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_SHT4x/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_SHT4x/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Python library for Sensirion SHT4x temperature and humidity sensors


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.

Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-sht4x/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-sht4x

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-sht4x

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-sht4x

Usage Example
=============

.. code-block:: python3

    import time
    import board
    import adafruit_sht4x

    i2c = board.I2C()   # uses board.SCL and board.SDA
    sht = adafruit_sht4x.SHT4x(i2c)
    print("Found SHT4x with serial number", hex(sht.serial_number))

    sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION
    # Can also set the mode to enable heater
    # sht.mode = adafruit_sht4x.Mode.LOWHEAT_100MS
    print("Current mode is: ", adafruit_sht4x.Mode.string[sht.mode])

    while True:
        temperature, relative_humidity = sht.measurements
        print("Temperature: %0.1f C" % temperature)
        print("Humidity: %0.1f %%" % relative_humidity)
        print("")
        time.sleep(1)


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_SHT4x/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
