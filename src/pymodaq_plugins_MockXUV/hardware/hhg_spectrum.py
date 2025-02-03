import h5py
from pathlib import Path

class HHG_Spectrum:
    def __init__(self, filename='HHG_20240402_Numerobis.h5'):
        self.filename = filename

        with h5py.File(Path(__file__).parent / filename, 'r') as f:
            data = f["Raw_datas"]["Detector000"]["Data1D"]["Ch000"]["Data"][()]

        self.data = data
