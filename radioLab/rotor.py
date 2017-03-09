
from .instrument import Instrument


class Rotor(Instrument):

    DEFAULT_ADDRESS = "GPIB::0::INSTR"
    NAME = "Generic Rotor"

    def __init__(self, address=DEFAULT_ADDRESS, **kwargs):
        super().__init__(address=address, **kwargs)

    @property
    def position(self):
        # should be implemented in subclass
        raise NotImplementedError

    @property
    def desired_position(self):
        # should be implemented in subclass
        raise NotImplementedError

    def move_absolute(self, position):
        # should be implemented in subclass
        raise NotImplementedError

    def move_relative(self, position):
        # should be implemented in subclass
        raise NotImplementedError


class NewportMM4005(Rotor):

    DEFAULT_ADDRESS = "GPIB::2::INSTR"
    NAME = "Newport MM4005 Motion Controller"

    def __init__(self, address=DEFAULT_ADDRESS, velocity=1, acceleration=1, debug=False, **kwargs):
        super().__init__(address=address, **kwargs)
        self._debug = debug
        self.velocity = velocity
        self.acceleration = acceleration

    @property
    def position(self):
        pos = self.query('4TP;')
        if self._debug:
            print('Position: %s' % pos)
        return pos

    @property
    def desired_position(self):
        pos = self.query('4DP;')
        if self._debug:
            print('Desired position: %s' % pos)
        return pos

    @property
    def velocity(self):
        vel = self.query('4DV;')
        if self._debug:
            print('Desired velocity: %s' % vel)
        return vel

    @velocity.setter
    def velocity(self, velocity):
        self.write('4VA%f;' % velocity)  # units/second

    @property
    def acceleration(self):
        return self.query('4DA;')

    @acceleration.setter
    def acceleration(self, acceleration):
        self.write('4AC%f;' % acceleration)

    def move_absolute(self, position):
        self.write('4PA%f;' % position)

    def move_relative(self, position):
        self.write('4PR%f;' % position)

    @property
    def idn(self):
        raise Warning("MM4005 doesn't implement standard GPIB command set")

    def wait_until_finished(self):
        raise Warning("MM4005 doesn't implement standard GPIB command set")
