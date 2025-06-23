import numpy as np

from pymodaq_plugins_datamixer.extensions.utils.model import DataMixerModel, np  # np will be used in method eval of the formula

from pymodaq_utils.math_utils import gauss1D, my_moment

from pymodaq_data.data import DataToExport, DataWithAxes
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_datamixer.extensions.utils.parser import (
    extract_data_names, split_formulae, replace_names_in_formula)


def gaussian_fit(x, amp, x0, dx, offset):
    return amp * gauss1D(x, x0, dx) + offset


class DataMixerModelDeltaR(DataMixerModel):
    params = [
        {'title': 'Get Data:', 'name': 'get_data', 'type': 'bool_push', 'value': False,
         'label': 'Get Data'},
        {'title': 'Do Background:', 'name': 'do_bkg', 'type': 'bool_push', 'value': False, 'label': 'Take Background'},
        {'title': 'XUV Camera:', 'name': 'camera', 'type': 'list', 'values': []},
        {'title': 'On/Off signal:', 'name': 'on_off_signal', 'type': 'list', 'values': []},
    ]

    def ini_model(self):
        self.update_data_list()
        self.bkg_poff = None
        self.bkg_pon = None
        self.doing_bkg = False

    def update_settings(self, param: Parameter):
        if param.name() == 'do_bkg':
            self.do_bkg()
        if param.name() == 'get_data':
            self.update_data_list()

    def update_data_list(self):
        dte = self.modules_manager.get_det_data_list()

        # data_list0D = dte.get_full_names('data0D')
        data_list1D = dte.get_full_names('data1D')
        data_list2D = dte.get_full_names('data2D')
        # data_listND = dte.get_full_names('dataND')

        # self.settings.child('data0D').setValue(dict(all_items=data_list0D, selected=[]))
        # self.settings.child('data1D').setValue(dict(all_items=data_list1D, selected=[]))
        self.settings.child('camera').setLimits(data_list2D)
        self.settings.child('camera').setValue(data_list2D[0])

        self.settings.child('on_off_signal').setLimits(data_list1D)
        self.settings.child('on_off_signal').setValue(data_list1D[0])
        # self.settings.child('dataND').setValue(dict(all_items=data_listND, selected=[]))

    def do_bkg(self):
        self.doing_bkg = True
        self.data_mixer.snap()

    def process_dte(self, dte: DataToExport):
        dte_processed = DataToExport('computed')

        if self.settings["camera"] is not '':
            dwa = dte.get_data_from_full_name(self.settings["camera"])

            dwa_onoff = dte.get_data_from_full_name(self.settings["on_off_signal"])
            first_is_on = dwa_onoff.isig[::2].mean() > dwa_onoff.isig[1::2].mean()

            if self.doing_bkg:
                if first_is_on:
                    self.bkg_poff = dwa.isig[1::2, :].mean(axis=0)
                    self.bkg_pon = dwa.isig[::2, :].mean(axis=0)
                else:
                    self.bkg_poff = dwa.isig[::2, :].mean(axis=0)
                    self.bkg_pon = dwa.isig[1::2, :].mean(axis=0)

                self.settings.child("do_bkg").setValue(False)
                self.doing_bkg = False

            else:
                if first_is_on:
                    poff = dwa.isig[1::2, :]
                    pon = dwa.isig[::2, :]
                else:
                    poff = dwa.isig[::2, :]
                    pon = dwa.isig[1::2, :]

                if self.bkg_poff is not None and self.bkg_pon is not None:
                    poff.data = [poff.data[0] - self.bkg_poff.data[0]]
                    pon.data = [pon.data[0] - self.bkg_pon.data[0]]

                dwa = ((pon-poff)/poff).mean(axis=0)
                dwa.name = "dR over R"
                dte_processed.append(dwa)

        return dte_processed



