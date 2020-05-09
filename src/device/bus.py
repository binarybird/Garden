import struct

from smbus2 import SMBus
import time
from src.device.interface import *

"""Mostly ripped from https://github.com/adafruit/Adafruit_Python_GPIO/blob/master/Adafruit_GPIO/I2C.py"""
class SimpleSMBus:
    _bus = None

    def __init__(self, dev: I2CDevice, force=False):
        self.dev = dev
        self.force = force
        pass

    def __enter__(self):
        if SimpleSMBus._bus is not None:
            raise Exception("Device conflict")
        print("Opening "+self.dev.get_name())
        SimpleSMBus._bus = SMBus(self.dev.get_bus_number(), self.force)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Closing "+self.dev.get_name())
        SimpleSMBus._bus.close()
        SimpleSMBus._bus = None

    def writeRaw8(self, value):
        """Write an 8-bit value on the bus (without register)."""
        value = value & 0xFF
        SimpleSMBus._bus.write_byte(self.dev.get_address(), value)

    def write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        value = value & 0xFF
        SimpleSMBus._bus.write_byte_data(self.dev.get_address(), register, value)

    def write16(self, register, value):
        """Write a 16-bit value to the specified register."""
        value = value & 0xFFFF
        SimpleSMBus._bus.write_word_data(self.dev.get_address(), register, value)

    def writeList(self, register, data):
        """Write bytes to the specified register."""
        SimpleSMBus._bus.write_i2c_block_data(self.dev.get_address(), register, data)

    def readList(self, register, length):
        """Read a length number of bytes from the specified register.  Results
        will be returned as a bytearray."""
        results = SimpleSMBus._bus.read_i2c_block_data(self.dev.get_address(), register, length)
        return results

    def readRaw8(self):
        """Read an 8-bit value on the bus (without register)."""
        result = SimpleSMBus._bus.read_byte(self.dev.get_address()) & 0xFF
        return result

    def readU8(self, register):
        """Read an unsigned byte from the specified register."""
        result = SimpleSMBus._bus.read_byte_data(self.dev.get_address(), register) & 0xFF
        return result

    def readS8(self, register):
        """Read a signed byte from the specified register."""
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result

    def readU16(self, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = SimpleSMBus._bus.read_word_data(self.dev.get_address(), register) & 0xFFFF
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self.readU16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def readU16LE(self, register):
        """Read an unsigned 16-bit value from the specified register, in little
        endian byte order."""
        return self.readU16(register, little_endian=True)

    def readU16BE(self, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self.readU16(register, little_endian=False)

    def readS16LE(self, register):
        """Read a signed 16-bit value from the specified register, in little
        endian byte order."""
        return self.readS16(register, little_endian=True)

    def readS16BE(self, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self.readS16(register, little_endian=False)




