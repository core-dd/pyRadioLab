

import pyvisa


class Instrument(object):

    DEFAULT_ADDRESS = 'GPIB::0::INSTR'
    NAME = 'Generic Instrument'

    def __init__(self, address=DEFAULT_ADDRESS, **kwargs):

        rm = pyvisa.ResourceManager(visa_library=kwargs.get('visa_library', ''))

        self.resource = rm.open_resource(address)
        self.resource.timeout = kwargs.get('timeout', 3000)

        # shortcuts
        self.write = self.resource.write
        self.read = self.resource.read
        self.query = self.resource.query
        self.query_values = self.resource.query_values

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.resource.close()

    @property
    def idn(self):
        return self.query('*IDN?')

    def wait_until_finished(self):
        self.query('*OPC?')
