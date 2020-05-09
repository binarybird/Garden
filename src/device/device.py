import RPi.GPIO as GPIO

from src.device.interface import *
from src.device.bus import SimpleSMBus
import time

muxer = None


def ensure_ivars(obj, ivars: []):
    errs = ""
    for ivar in ivars:
        if not hasattr(obj, ivar):
            errs += ("Missing ivar: " + ivar + " ")
    if len(errs) == 0:
        return
    raise KeyError(errs)


class WaterValve(Pollable):

    @staticmethod
    def get_expected_args():
        return ['enabled']

    def init(self, args: {}):
        for k, v in args.items():
            setattr(self, k, v)
        ensure_ivars(self, WaterValve.get_expected_args())

    def initialize(self):
        pass

    def poll(self):
        return {'enabled': self.enabled}


class SHT20(I2CMuxDevice):
    TEMPERATURE_NO_HOLD = 0xF3
    HUMIDITY_NO_HOLD = 0xF5
    TEMPERATURE_HOLD = 0xE3
    HUMIDITY_HOLD = 0xE5
    WRITE_REGISTER = 0xE6
    READ_REGISTER = 0xE7
    SOFT_RESET = 0xFE

    @staticmethod
    def get_expected_args():
        return ['bus', 'name', 'mux_channel', 'mux_address']

    def __init__(self, args: {}):
        self.address = 0x40
        for k, v in args.items():
            setattr(self, k, v)
        ensure_ivars(self, SHT20.get_expected_args())

    def initialize(self):
        pass

    def poll(self, **kwargs):
        with SimpleSMBus(self) as bus:
            bus.writeRaw8(SHT20.TEMPERATURE_NO_HOLD)
            time.sleep(0.5)
            data0 = bus.readRaw8()
            data1 = bus.readRaw8()

            temp = data0 * 256 + data1
            cTemp = -46.85 + ((temp * 175.72) / 65536.0)

            bus.writeRaw8(SHT20.HUMIDITY_NO_HOLD)
            time.sleep(0.5)

            data0 = bus.readRaw8()
            data1 = bus.readRaw8()

            humidity = data0 * 256 + data1
            humidity = -6 + ((humidity * 125.0) / 65536.0)

        return {'humidity': {humidity:"%"}, 'temperature': {cTemp:"c"}}

    def get_mux_channel(self):
        return self.mux_channel

    def get_mux_address(self):
        return self.mux_address

    def get_bus_number(self):
        return self.bus

    def get_address(self):
        return self.address

    def get_name(self):
        return self.name

"""Mostly ripped from https://github.com/adafruit/Adafruit_Python_BMP/blob/master/Adafruit_BMP/BMP085.py"""
class BMP180(I2CMuxDevice):
    # Operating Modes
    ULTRALOWPOWER = 0
    STANDARD = 1
    HIGHRES = 2
    ULTRAHIGHRES = 3

    # BMP085 Registers
    CAL_AC1 = 0xAA  # R   Calibration data (16 bits)
    CAL_AC2 = 0xAC  # R   Calibration data (16 bits)
    CAL_AC3 = 0xAE  # R   Calibration data (16 bits)
    CAL_AC4 = 0xB0  # R   Calibration data (16 bits)
    CAL_AC5 = 0xB2  # R   Calibration data (16 bits)
    CAL_AC6 = 0xB4  # R   Calibration data (16 bits)
    CAL_B1 = 0xB6  # R   Calibration data (16 bits)
    CAL_B2 = 0xB8  # R   Calibration data (16 bits)
    CAL_MB = 0xBA  # R   Calibration data (16 bits)
    CAL_MC = 0xBC  # R   Calibration data (16 bits)
    CAL_MD = 0xBE  # R   Calibration data (16 bits)
    CONTROL = 0xF4
    TEMPDATA = 0xF6
    PRESSUREDATA = 0xF6

    # Commands
    READTEMPCMD = 0x2E
    READPRESSURECMD = 0x34

    @staticmethod
    def get_expected_args():
        return ['bus', 'name', 'mux_channel', 'mux_address']

    def __init__(self, args: {}):
        self.address = 0x77
        self._mode = BMP180.ULTRAHIGHRES
        for k, v in args.items():
            setattr(self, k, v)
        ensure_ivars(self, BMP180.get_expected_args())

    def initialize(self):
        with SimpleSMBus(self) as bus:
            self.cal_AC1 = bus.readS16BE(BMP180.CAL_AC1)   # INT16
            self.cal_AC2 = bus.readS16BE(BMP180.CAL_AC2)   # INT16
            self.cal_AC3 = bus.readS16BE(BMP180.CAL_AC3)   # INT16
            self.cal_AC4 = bus.readU16BE(BMP180.CAL_AC4)   # UINT16
            self.cal_AC5 = bus.readU16BE(BMP180.CAL_AC5)   # UINT16
            self.cal_AC6 = bus.readU16BE(BMP180.CAL_AC6)   # UINT16
            self.cal_B1 = bus.readS16BE(BMP180.CAL_B1)     # INT16
            self.cal_B2 = bus.readS16BE(BMP180.CAL_B2)     # INT16
            self.cal_MB = bus.readS16BE(BMP180.CAL_MB)     # INT16
            self.cal_MC = bus.readS16BE(BMP180.CAL_MC)     # INT16
            self.cal_MD = bus.readS16BE(BMP180.CAL_MD)     # INT16

    def poll(self):
        t = self.read_temperature()
        p = self.read_pressure()
        return{"pressure":{p/100:"mb"},"temperature":{t:"c"}}

    def read_raw_temp(self):
        """Reads the raw (uncompensated) temperature from the sensor."""
        with SimpleSMBus(self) as bus:
            bus.write8(BMP180.CONTROL, BMP180.READTEMPCMD)
            time.sleep(0.005)  # Wait 5ms
            raw = bus.readU16BE(BMP180.TEMPDATA)
        return raw

    def read_raw_pressure(self):
        """Reads the raw (uncompensated) pressure level from the sensor."""
        with SimpleSMBus(self) as bus:
            bus.write8(BMP180.CONTROL, BMP180.READPRESSURECMD + (self._mode << 6))
            if self._mode == BMP180.ULTRALOWPOWER:
                time.sleep(0.005)
            elif self._mode == BMP180.HIGHRES:
                time.sleep(0.014)
            elif self._mode == BMP180.ULTRAHIGHRES:
                time.sleep(0.026)
            else:
                time.sleep(0.008)
            msb = bus.readU8(BMP180.PRESSUREDATA)
            lsb = bus.readU8(BMP180.PRESSUREDATA + 1)
            xlsb = bus.readU8(BMP180.PRESSUREDATA + 2)
            raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self._mode)
        return raw

    def read_temperature(self):
        """Gets the compensated temperature in degrees celsius."""
        UT = self.read_raw_temp()
        # Datasheet value for debugging:
        # UT = 27898
        # Calculations below are taken straight from section 3.5 of the datasheet.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) // (X1 + self.cal_MD)
        B5 = X1 + X2
        temp = ((B5 + 8) >> 4) / 10.0
        return temp

    def read_pressure(self):
        """Gets the compensated pressure in Pascals."""
        UT = self.read_raw_temp()
        UP = self.read_raw_pressure()
        # Datasheet values for debugging:
        # UT = 27898
        # UP = 23843
        # Calculations below are taken straight from section 3.5 of the datasheet.
        # Calculate true temperature coefficient B5.
        X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
        X2 = (self.cal_MC << 11) // (X1 + self.cal_MD)
        B5 = X1 + X2
        # Pressure Calculations
        B6 = B5 - 4000
        X1 = (self.cal_B2 * (B6 * B6) >> 12) >> 11
        X2 = (self.cal_AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.cal_AC1 * 4 + X3) << self._mode) + 2) // 4
        X1 = (self.cal_AC3 * B6) >> 13
        X2 = (self.cal_B1 * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.cal_AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> self._mode)
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        return p

    def read_altitude(self, sealevel_pa=101325.0):
        """Calculates the altitude in meters."""
        # Calculation taken straight from section 3.6 of the datasheet.
        pressure = float(self.read_pressure())
        altitude = 44330.0 * (1.0 - pow(pressure / sealevel_pa, (1.0 / 5.255)))
        return altitude

    def read_sealevel_pressure(self, altitude_m=0.0):
        """Calculates the pressure at sealevel when given a known altitude in
        meters. Returns a value in Pascals."""
        pressure = float(self.read_pressure())
        p0 = pressure / pow(1.0 - altitude_m / 44330.0, 5.255)
        return p0

    def get_mux_channel(self):
        return self.mux_channel

    def get_mux_address(self):
        return self.mux_address

    def get_bus_number(self):
        return self.bus

    def get_address(self):
        return self.address

    def get_name(self):
        return self.name


class TCA9548A(I2CDevice):
    CHANNEL_0 = 0x01
    CHANNEL_1 = 0x02
    CHANNEL_2 = 0x04
    CHANNEL_3 = 0x08
    CHANNEL_4 = 0x10
    CHANNEL_5 = 0x20
    CHANNEL_6 = 0x40
    CHANNEL_7 = 0x80

    @staticmethod
    def get_expected_args():
        return ['bus', 'address', 'name', 'A0', 'A1', 'A2']

    def __init__(self, args: {}):
        self.A0 = 13
        self.A1 = 19
        self.A2 = 26
        for k, v in args.items():
            if v is None:
                continue
            setattr(self, k, v)

        ensure_ivars(self, TCA9548A.get_expected_args())

    def initialize(self):
        pass

    def get_bus_number(self):
        return self.bus

    def get_address(self):
        return self.address

    def get_name(self):
        return self.name

    def poll(self, **kwargs):
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
    arg = {'bus': 1, 'address': 0x70, 'name': 'Muxer'}
    muxer = TCA9548A(arg)

    return muxer


def change_mux_channel(mux: TCA9548A, dev: I2CMuxDevice):
    with SimpleSMBus(mux) as bus:
        bus.writeRaw8(dev.get_mux_channel())
