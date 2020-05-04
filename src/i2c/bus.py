from smbus2 import SMBus
from src.i2c.interface import *


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
        pass

    def rb(self):
        print("Read@ "+hex(self.dev.get_address()))
        return SimpleSMBus._bus.read_byte(self.dev.get_address())

    def wb(self, byte):
        print("Write@ " + hex(self.dev.get_address()) + " value: "+hex(byte))
        SimpleSMBus._bus.write_byte(self.dev.get_address(), byte)