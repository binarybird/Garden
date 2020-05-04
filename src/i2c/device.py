import RPi.GPIO as GPIO
from src.i2c.interface import *
from src.i2c.bus import SimpleSMBus
import time

muxer = None


class SHT20(I2CMuxDevice):
    TEMPERATURE_NO_HOLD = 0xF3
    HUMIDITY_NO_HOLD = 0xF5
    TEMPERATURE_HOLD = 0xE3
    HUMIDITY_HOLD = 0xE5
    WRITE_REGISTER = 0xE6
    READ_REGISTER = 0xE7
    SOFT_RESET = 0xFE

    def __init__(self, mux_channel, mux_address, name, bus=1, address=0x40):
        self.bus = bus
        self.address = address
        self.name = name
        self.mux_channel = mux_channel
        self.mux_address = mux_address

    def get_bus_number(self):
        return self.bus

    def get_address(self):
        return self.address

    def get_mux_channel(self):
        return self.mux_channel

    def get_mux_address(self):
        return self.mux_address

    def get_name(self):
        return self.name

    def poll(self):
        with SimpleSMBus(self) as bus:
            bus.wb(SHT20.TEMPERATURE_NO_HOLD)
            time.sleep(0.5)
            data0 = bus.rb()
            data1 = bus.rb()

            temp = data0 * 256 + data1
            cTemp = -46.85 + ((temp * 175.72) / 65536.0)

            bus.wb(SHT20.HUMIDITY_NO_HOLD)
            time.sleep(0.5)

            data0 = bus.rb()
            data1 = bus.rb()

            humidity = data0 * 256 + data1
            humidity = -6 + ((humidity * 125.0) / 65536.0)

        return {'humidity': humidity, 'temperature': cTemp}


class TCA9548A(I2CDevice):

    CHANNEL_0 = 0x01
    CHANNEL_1 = 0x02
    CHANNEL_2 = 0x04
    CHANNEL_3 = 0x08
    CHANNEL_4 = 0x10
    CHANNEL_5 = 0x20
    CHANNEL_6 = 0x40
    CHANNEL_7 = 0x80

    def __init__(self, address, name, bus=1, A0_pin=13, A1_pin=19, A2_pin=26):
        self.address = address
        self.bus = bus
        self.name = name
        self.A0 = A0_pin
        self.A1 = A1_pin
        self.A2 = A2_pin

    def get_bus_number(self):
        return self.bus

    def get_address(self):
        return self.address

    def get_name(self):
        return self.name

    def poll(self):
        return {}

    def get_address_gpio(self):
        if self.address == 0x70:
            return {self.A0: GPIO.LOW,
                    self.A1: GPIO.LOW,
                    self.A2: GPIO.LOW}
        elif self.address == 0x71:
            return {self.A0: GPIO.HIGH,
                    self.A1: GPIO.LOW,
                    self.A2: GPIO.LOW}
        elif self.address == 0x72:
            return {self.A0: GPIO.LOW,
                    self.A1: GPIO.HIGH,
                    self.A2: GPIO.LOW}
        elif self.address == 0x73:
            return {self.A0: GPIO.HIGH,
                    self.A1: GPIO.HIGH,
                    self.A2: GPIO.LOW}
        elif self.address == 0x74:
            return {self.A0: GPIO.LOW,
                    self.A1: GPIO.LOW,
                    self.A2: GPIO.HIGH}
        elif self.address == 0x75:
            return {self.A0: GPIO.HIGH,
                    self.A1: GPIO.LOW,
                    self.A2: GPIO.HIGH}
        elif self.address == 0x76:
            return {self.A0: GPIO.LOW,
                    self.A1: GPIO.HIGH,
                    self.A2: GPIO.HIGH}
        elif self.address == 0x77:
            return {self.A0: GPIO.HIGH,
                    self.A1: GPIO.HIGH,
                    self.A2: GPIO.HIGH}
        else:
            raise Exception("Unknown state")


def get_muxer():
    global muxer
    if muxer is not None:
        return muxer

    muxer = TCA9548A(0x70, "Muxer")
    return muxer


def change_mux_channel(mux: TCA9548A, dev: I2CMuxDevice):
    with SimpleSMBus(mux) as bus:
        bus.wb(dev.get_mux_channel())
