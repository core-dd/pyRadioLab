
import numpy as np
import time


class AntennaPatternSweep(object):

    def __init__(self, vna, rotor, start_angle=-180, stop_angle=180, mode="continuous", debug=False, **kwargs):
        self._debug = debug

        self._vna = vna
        self._rotor = rotor

        self._start_angle = start_angle
        self._stop_angle = stop_angle
        self._angle_accuracy = kwargs.get('angle_accuracy', 0.1)

        if mode is not 'continuous':
            raise NotImplementedError("Only continuous sweep implemented")
        self._mode = mode

    @property
    def start_angle(self):
        return self._start_angle

    @start_angle.setter
    def start_angle(self, angle):
        # angle in degrees
        self._start_angle = angle

    @property
    def stop_angle(self):
        return self._start_angle

    @stop_angle.setter
    def stop_angle(self, angle):
        # angle in degrees
        self._stop_angle = angle

    def log_timestamped(self, message):
        print('[%s]:\t%s' % (time.strftime('%H:%m'), message))

    def run(self):
        if self._mode is 'continuous':
            self._run_continuous()

    def _run_continuous(self):
        t_start = time.localtime()
        orig_position = self._rotor.position
        self.log_timestamped('Starting a rotor sweep measurement collecting data continuously')

        self.log_timestamped('Moving to start position')
        self._rotor.move_absolute(self._start_angle)
        while self._rotor.position - self._start_angle < self._angle_accuracy:
            if self._debug:
                print("\tPosition: %f" % self._rotor.position)
            time.sleep(1)
        self.log_timestamped('Start position reached')

        positions = []
        data = []
        self.log_timestamped('Starting sweep whilst collecting data')
        self._rotor.move_absolute(self._stop_angle)
        while self._rotor.position - self._stop_angle < self._angle_accuracy:
            # TODO: progress bar :)
            positions.append(self._rotor.position)
            data.append(self._vna.read_data())
        self.log_timestamped('End position reached')
        self.log_timestamped('Collected %i data points' % (len(data)))

        self.log_timestamped('Moving to original position')
        while self._rotor.position - orig_position < self._angle_accuracy:
            if self._debug:
                print("\tPosition: %f" % self._rotor.position)
            time.sleep(1)
        self.log_timestamped('Original position reached')

        t_stop = time.localtime()
        self.log_timestamped('Continuous sweep finished in %i seconds' % (t_stop - t_start))

        return np.array(positions), np.array(data)

