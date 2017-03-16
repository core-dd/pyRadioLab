
from .instrument import Instrument

import numpy as np


class HP8510(Instrument):

    DEFAULT_ADDRESS = 'GPIB::16::INSTR'
    NAME = 'HP8510'

    DATA_TRANSFER_FORMATS = (
        'FORM1',  # only raw data, fast CW mode, fastest transfer format
        'FROM2',  # 32-bit IEEE 728 floating point '>c8'
        'FORM3',  # 64-bit IEEE 728 floating point '>c16'
        'FORM4',  # ASCII, slowest transfer format
        'FORM5',  # 32-bit DOS compatible floating point
    )

    SCATTERING_PARAMETERS = ('S11', 'S21', 'S12', 'S22')

    def __init__(self, address=DEFAULT_ADDRESS, **kwargs):
        super().__init__(address=address, **kwargs)
        self._debug = kwargs.get('debug', False)

        # initialise VNA
        self._transfer_format = ''
        self.transfer_format = kwargs.get('transfer_format', 'FORM3')           # work with FORM3 as standard setting
        self._s_parameter = ''
        self.s_parameter = kwargs.get('scattering_parameter', 'S11')
        self._frequencies = np.array([1e9])
        self.set_frequency_list(kwargs.get('frequencies', np.array([1e9])))
        self.write('LOGM;')                                                     # cartesian log mag format on VNA screen

    def _parse_data(self, command):
        # TODO: investigate pyVISA helpers to read binary data
        self.write(command)
        raw_data = self.resource.read_raw()
        if self._debug:
            print(raw_data)

        if self._transfer_format is 'FORM2':
            # parse header, size (two-byte number) [in # of bytes] and payload (re/im pairs of 32 bit IEEE 728 FP)
            header = raw_data[:2]
            size = raw_data[2:4]
            payload = np.fromstring(raw_data[4:], dtype='>c18')  # '>c8' big endian complex 64 bit
        elif self._transfer_format is 'FORM3':
            # parse header, size (two-byte number) [in # of bytes] and payload (re/im pairs of 64 bit IEEE 728 FP)
            header = raw_data[:2]
            size = raw_data[2:4]
            payload = np.fromstring(raw_data[4:], dtype='>c16')  # '>c16' big endian complex 128 bit
        else:
            raise NotImplementedError

        return payload

    def read_data(self):
        return self._parse_data('OUTPDATA;')

    @property
    def transfer_format(self):
        return self._transfer_format

    @transfer_format.setter
    def transfer_format(self, transfer_format):
        if transfer_format in self.DATA_TRANSFER_FORMATS:
            self.write(transfer_format+';')
            self._transfer_format = transfer_format
        else:
            raise EnvironmentError("%s is not a valid transfer format" % transfer_format)

    @property
    def frequencies(self):
        return self._frequencies

    def set_frequency_list(self, frequencies):
        # define single frequencies for measurement setup
        if len(frequencies) > 10:
            print("WARNING: not tested behaviour")

        # see procedure HP8510 Keyword Directory E-5
        self.write('EDITLIST;')
        self.write('CLEL;')                 # clear edit list
        for f in frequencies:               # adding frequency list segments
            # TODO: sanity check of f
            self.write('SADD;')
            self.write('STAR %f;' % f)
            self.write('STOP %f;' % f)
            self.write('POIN 1;')
            self.write('SDON;')
        self.write('EDITDONE;')
        self.write('LISFREQ;')              # frequency list sweep mode

        self._frequencies = frequencies

    # TODO: function to define one frequency set via start, stop & number of points

    # XXX: just working with channel 1 for simplicity
    @property
    def s_parameter(self):
        return self._s_parameter

    @s_parameter.setter
    def s_parameter(self, parameter):
        if parameter in self.SCATTERING_PARAMETERS:
            self.write(parameter+';')
            self._s_parameter = parameter
        else:
            raise ValueError("Scattering parameter %s not know to HP8510. Choose between S11, S21, S12, S22!")
