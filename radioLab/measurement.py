
from datetime import datetime
import numpy as np
from time import sleep
from tqdm import tqdm

class AntennaPatternSweep(object):

    def __init__(self, vna, rotor, start_angle=-180, stop_angle=180, mode="continuous", debug=False, **kwargs):
        self._debug = debug

        self._vna = vna
        self._rotor = rotor

        self._start_angle = start_angle
        self._stop_angle = stop_angle
        self._angle_accuracy = kwargs.get('angle_accuracy', 0.1)
        self._positioning_velocity = kwargs.get('positioning_velocity', 8)
        self._sweep_velocity= kwargs.get('sweep_velocity', 3)

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
        print('[%s]:\t%s' % (datetime.now().strftime('%H:%M:%S'), message))

    def run(self):
        if self._mode is 'continuous':
            return self._run_continuous()

    def _run_continuous(self):
        t_start = datetime.now()
        orig_position = self._rotor.position
        self.log_timestamped('Starting a rotor sweep measurement collecting data continuously')

        pbar = tqdm(desc='Moving to start position', total=np.abs(self._start_angle-orig_position), unit=' deg',
                    dynamic_ncols=True)
        last_pos = self._rotor.position
        curr_pos = last_pos
        self._rotor.velocity = self._positioning_velocity
        self._rotor.move_absolute(self._start_angle)
        while np.abs(self._rotor.position - self._start_angle) > self._angle_accuracy:
            curr_pos = self._rotor.position
            pbar.update(np.abs(curr_pos-last_pos))
            last_pos = curr_pos
            if self._debug:
                print("\tPosition: %f" % self._rotor.position)
            sleep(1)
        pbar.update(np.abs(last_pos - self._rotor.position))
        pbar.close()
        self.log_timestamped('Start position reached')
        sleep(2)

        positions = []
        data = []
        self.log_timestamped('Starting sweep whilst collecting data')

        pbar = tqdm(desc='Moving to end position', total=np.abs(self._stop_angle-self._start_angle), unit=' deg',
                    dynamic_ncols=True)
        last_pos = self._rotor.position
        curr_pos = last_pos
        self._rotor.velocity = self._sweep_velocity
        self._rotor.move_absolute(self._stop_angle)
        while np.abs(self._rotor.position - self._stop_angle) > self._angle_accuracy:
            curr_pos = self._rotor.position
            pbar.update(np.abs(curr_pos-last_pos))
            last_pos = curr_pos
            positions.append(self._rotor.position)
            data.append(self._vna.read_data())
        pbar.update(np.abs(last_pos - self._rotor.position))
        pbar.close()
        self.log_timestamped('End position reached')
        self.log_timestamped('Collected %i data points' % (len(data)))

        sleep(1)
        pbar = tqdm(desc='Moving to original position', total=np.abs(orig_position-self._stop_angle), unit=' deg',
                    dynamic_ncols=True)
        last_pos = self._rotor.position
        curr_pos = last_pos
        self._rotor.velocity = self._positioning_velocity
        self._rotor.move_absolute(orig_position)
        while np.abs(self._rotor.position - orig_position) > self._angle_accuracy:
            curr_pos = self._rotor.position
            pbar.update(np.abs(curr_pos-last_pos))
            last_pos = curr_pos
            if self._debug:
                print("\tPosition: %f" % self._rotor.position)
            sleep(1)
        pbar.update(np.abs(last_pos - self._rotor.position))
        pbar.close()
        self.log_timestamped('Original position reached')

        t_stop = datetime.now()
        self.log_timestamped('Continuous sweep finished in %s' % str(t_stop - t_start))

        return np.array(positions), np.array(data)

