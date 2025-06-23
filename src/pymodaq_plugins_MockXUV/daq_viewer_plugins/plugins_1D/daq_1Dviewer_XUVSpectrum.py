import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, Axis, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_MockXUV.hardware.hhg_spectrum import HHG_Spectrum


class DAQ_1DViewer_XUVSpectrum(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
    """
    params = comon_parameters+[
        {'title': 'Image', 'name': 'roi', 'type': 'group', 'children':
            [{'title': 'Height', 'name': 'height', 'type': 'int', 'value': 1},
             {'title': 'Bottom', 'name': 'bottom', 'type': 'int', 'value': 0},
             {'title': 'Width', 'name': 'width', 'type': 'int', 'value': 2048},
             {'title': 'Left', 'name': 'left', 'type': 'int', 'value': 0},
             {'title': 'Auto Vertical Centering', 'name': 'auto_vert', 'type': 'bool', 'value': False},
             {'title': 'Update ROI', 'name': 'update_roi', 'type': 'bool_push', 'value': False},
             {'title': 'Clear ROI+Bin', 'name': 'clear_roi', 'type': 'bool_push', 'value': False},
             {'title': 'Binning', 'name': 'binning', 'type': 'list', 'limits': [1, 2]}, ]
         },
        {'title': 'Set Background', 'name': 'take_background', 'type': 'bool_push', 'value': False},

        {'title': 'Timing', 'name': 'timing_opts', 'type': 'group', 'children':
            [{'title': 'Exposure Time (ms)', 'name': 'exposure_time', 'type': 'float', 'value': 0.13},
             {'title': 'Chunk size', 'name': 'chunk_size', 'type': 'int', 'value': 1000},
             {'title': 'Compute FPS', 'name': 'fps_on', 'type': 'bool', 'value': True},
             {'title': 'Actual FPS', 'name': 'fps', 'type': 'float', 'value': 0.0, 'readonly': True, 'decimals': 6},
             {'title': 'Max FPS', 'name': 'fps2', 'type': 'float', 'value': 0.0, 'readonly': True, 'decimals': 6},
             {'title': 'NLevel:', 'name': 'amp_noise', 'type': 'float', 'value': 2000, 'default': 2000, 'min': 0},
             {'title': 'SLevel:', 'name': 'shift_noise', 'type': 'float', 'value': 5, 'default': 5, 'min': 0}],
        },
        ]

    def ini_attributes(self):
        #  autocompletion
        self.background = np.empty(0)
        self.controller: HHG_Spectrum = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "take_background":
            self.take_background()

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
            self.controller = HHG_Spectrum()

        # # get the x_axis (you may want to to this also in the commit settings if x_axis may have changed
        # data_x_axis = self.controller.your_method_to_get_the_x_axis()  # if possible
        self.x_axis = Axis(data=np.arange(self.controller.data.shape[0]), label='Pixels', units='', index=0)

        self.dte_signal_temp.emit(DataToExport(name='HHG',
                                               data=[DataFromPlugins(name='Mock1',
                                                                     data=[self.controller.data]),
                                                                           ],
                                                                     dim='Data1D', labels=['XUV'],
                                                                     axes=[self.x_axis]))

        info = "Whatever info you want to log"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        pass

    def take_background(self):
        bkg = np.ones_like(self.x_axis.get_data())*5.5
        self.background = bkg
        self.dte_signal.emit(DataToExport('HHG',
                                          data=[DataFromPlugins(name='Mock1', data=bkg,
                                                                dim='Data1D', labels=['background'],
                                                                axes=[self.x_axis], do_plot=False, do_save=True)]))


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


        ##synchrone version (blocking function)
        data_tot = self.controller.data.copy() + self.settings['timing_opts', 'amp_noise'] * np.random.rand((self.x_axis.size))
        x = self.x_axis.get_data()
        data_tot = np.interp(x, x +self.settings['timing_opts', 'shift_noise']*np.random.randn(1), data_tot)

        self.dte_signal.emit(DataToExport('HHG',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data1D', labels=['data'],
                                                                axes=[self.x_axis])]))


    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        return ''


if __name__ == '__main__':
    main(__file__)
