import time

import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins
from pymodaq_plugins_MockXUV.hardware.cmos_simulator import Mock_SingleShot
import random


class DAQ_2DViewer_MockStabCamera(DAQ_Viewer_base):
    """ Instrument plugin class for a 2D viewer.
    """
    params = comon_parameters + [
        {'title': 'Chunk size', 'name': 'chunk_size', 'type': 'int', 'value': 100},
        {'title': 'Sleep time', 'name': 'sleep_time', 'type': 'int', 'value': 10},
        {'title': 'White noise:', 'name': 'amp_noise', 'type': 'float', 'value': 0.1, 'default': 0.1, 'min': 0},
        #{'title': '2D Image:', 'name': 'twod_image', 'type': 'bool', 'value': True, 'default': True},
    ]

    def ini_attributes(self):
        self.controller: Mock_SingleShot = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "a_parameter_you've_added_in_self.params":
            self.controller.your_method_to_apply_this_param_change()
        # elif ...

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        self.ini_detector_init(slave_controller=controller)

        if self.is_master:
            self.controller = Mock_SingleShot()  # instantiate you driver with whatever arguments are needed

        self.set_axes()
        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def set_axes(self):
        data_x_axis = np.arange(len(self.controller.pon))
        self.x_axis = Axis(data=data_x_axis, label='Pixels', units='', index=0)

        data_y_axis = np.arange(self.settings["chunk_size"])  # if possible
        self.y_axis = Axis(data=data_y_axis, label='Shot', units='', index=1)

    def close(self):
        """Terminate the communication protocol"""

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        time.sleep(self.settings["sleep_time"] / 1000)
        data_tot = self.controller.grab_stab(self.settings["chunk_size"] // 2)

        data_tot += self.settings['amp_noise'] * np.random.random_sample(data_tot.shape)


        dfp_list = [DataFromPlugins(name='Camera', data=[data_tot],
                                            dim='Data2D', labels=['label1'],
                                            x_axis=self.x_axis, y_axis=self.y_axis)]
        self.dte_signal.emit(DataToExport('CMOS', data=dfp_list))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        return ''


if __name__ == '__main__':
    main(__file__)
