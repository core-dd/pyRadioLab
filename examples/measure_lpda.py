
from radioLab import HP8510, NewportMM4005, AntennaPatternSweep

from datetime import datetime
import numpy as np

vna = HP8510()
rot = NewportMM4005(velocity=8)
experiment = AntennaPatternSweep(vna, rot)
vna.s_parameter = 'S12'

vna.set_frequency_list(np.array([1472, 2400, 2560, 3820, 4160, 5915]) * 1e6)

positions, data = experiment.run()

time_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
np.save('%s_positions' % time_stamp, positions)
np.save('%s_data' % time_stamp, data)
