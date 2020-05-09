
class Pollable:
    def initialize(self):
        raise NotImplementedError()

    def poll(self):
        raise NotImplementedError()


class I2CDevice(Pollable):
    def get_bus_number(self):
        raise NotImplementedError()

    def get_address(self):
        raise NotImplementedError()

    def get_name(self):
        raise NotImplementedError()


class I2CMuxDevice(I2CDevice):
    def get_mux_channel(self):
        raise NotImplementedError()

    def get_mux_address(self):
        raise NotImplementedError()
