
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
        self._max_velocity = kwargs.get('max_velocity', 8.0)
        self._debug = debug
        self.velocity = velocity
        self.acceleration = acceleration

    @property
    def position(self):
        pos = self.query('4TP;')[3:]
        if self._debug:
            print('Position: %s' % pos)
        return float(pos)

    @property
    def desired_position(self):
        pos = self.query('4DP;')[3:]
        if self._debug:
            print('Desired position: %s' % pos)
        return float(pos)

    @property
    def velocity(self):
        vel = self.query('4DV;')[3:]
        if self._debug:
            print('Desired velocity: %s' % vel)
        return float(vel)

    @velocity.setter
    def velocity(self, velocity):
        if 0 < velocity <= self._max_velocity:
            self.write('4VA%.1f;' % velocity)  # units/second
        else:
            print('WARNING: %f is out of velocity bounds (0, %f) - command discarded' % (velocity, self._max_velocity))

    @property
    def acceleration(self):
        return float(self.query('4DA;')[3:])

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
