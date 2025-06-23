import numpy as np
from pathlib import Path
import random


class Mock_SingleShot:

    def __init__(self, filename='ponoff_transient.npy'):
        self.filename = filename
        data = np.load(Path(__file__).parent / self.filename)

        self.pon = data[1, :]
        self.poff = data[0, :]

        self.bkg_on = np.ones_like(self.pon) * 4000
        self.bkg_off = np.ones_like(self.poff) * 2000

        self.stabpoff = 0.0 * np.ones((1024, 1))  # Simulated data for pump off
        self.stabpon = 1.0 * np.ones((1024, 1))  # Simulated data for pump on

        self.FirstShotIsPumpOn = random.choice([True, False])

    def grab_XUV(self, nframes, gas_off=False):
        """Simulate grabbing data from the camera."""
        # Simulated data for demonstration purposes
        self.FirstShotIsPumpOn = random.choice([True, False])

        if gas_off:
            data_oneshot = np.vstack((self.bkg_off, self.bkg_on))
        else:
            data_oneshot = np.vstack((self.poff, self.pon))

        if self.FirstShotIsPumpOn:
            data_oneshot = np.flip(data_oneshot, axis=0)  # flip the data so that the first shot is pump on

        data_tot = np.tile(data_oneshot, (nframes, 1))

        return data_tot

    def grab_stab(self, nframes):
        """Simulate grabbing data from the camera."""
        # Simulated data for demonstration purposes
        stab_data = np.tile(np.hstack((self.stabpon, self.stabpoff)), nframes).T
        if not self.FirstShotIsPumpOn:
            stab_data = np.roll(stab_data, shift=1, axis=0)

        return stab_data


