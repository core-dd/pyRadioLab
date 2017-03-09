
import visa


class Rotor(object):

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

    def __init__(self, gpib_address="GPIB0::2::INSTR", velocity=1, acceleration=1, debug=False):
        self._debug = debug
        self._gpib_address = gpib_address
        self._instrument = visa.open_resource(gpib_address)
        if self._debug:
            print(self._instrument.query('*IDN?'))

        self.velocity = velocity
        self.acceleration = acceleration

    @property
    def position(self):
        pos = self._instrument.query('4TP;')
        if self._debug:
            print('Position: %s' % pos)
        return pos

    @property
    def desired_position(self):
        pos = self._instrument.query('4DP;')
        if self._debug:
            print('Desired position: %s' % pos)
        return pos

    @property
    def velocity(self):
        vel = self._instrument.query('4DV;')
        if self._debug:
            print('Desired velocity: %s' % vel)
        return vel

    @velocity.setter
    def velocity(self, velocity):
        self._instrument.write('4VA%f;' % velocity)  # units/second

    @property
    def acceleration(self):
        return self._instrument.query('4DA;')

    @acceleration.setter
    def acceleration(self, acceleration):
        self._instrument('4AC%f;' % acceleration)

    def move_absolute(self, position):
        self._instrument.write('4PA%f;' % position)

    def move_relative(self, position):
        self._instrument.write('4PR%f;' % position)
