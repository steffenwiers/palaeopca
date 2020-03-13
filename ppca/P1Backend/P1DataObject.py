# Imports
import numpy as np


class P1DataObject(object):
    def __init__(self):
        self.__data = None
        self.__samples = None
        self.__steps = None
        self.__volume = 10
        self.__units = "emu"

    def load_data(self, infile: str, sep: str, skip_header: int = 0):
        data = np.genfromtxt(infile, delimiter = sep, skip_header = skip_header)
        data = data.reshape(len(np.unique(data[:, 0])), len(np.unique(data[:, 1])), data.shape[1])

        self.__data = data
        self.__samples = data[:, 0, 0]
        self.__steps = data[0, :, 1]

    def set_volume(self, volume = 10):
        """
        Set sample volume.

        Keywords:
            volume: volume in g/cc
        """
        self.__volume = volume

    def set_units(self, units: str):
        self.__units = units

    def get_units(self):
        return self.__units

    def convert_units(self, new_units):
        """
        Sets input and output units. Converts from input to output.

        Keywords:
            units_in: input units
            units_out: output_units

        Possible units: emu, Am2, A/m
        """        
        if self.__units == "emu" and units_out == "Am2":
            self.__data[:, :, 2:] = self.__data[:, :, 2:] * 10**(-3)
        elif self.__units == "emu" and units_out == "A/m":
            self.__data[:, :, 2:] = self.__data[:, :, 2:] / self.__volume * 10**(3)
        elif self.__units == "Am2" and units_out == "emu":
            self.__data[:, :, 2:] = self.__data[:, :, 2:] * 10**(3)
        elif self.__units == "A/m" and units_out == "emu":
            self.__data[:, :, 2:] = self.__data[:, :, 2:] * self.__volume * 10**(-3)

        self.__units = new_units

    def get_units(self):
        return self.__units

    def get_volume(self):
        return self.__volume
        
    def get_steps(self) -> np.ndarray:
        return self.__steps

    def get_samples(self) -> np.ndarray:
        return self.__samples

    def get_data(self, sample: str) -> np.ndarray:
        samples = [str(x) for x in self.get_samples()]
        return self.__data[samples.index(str(sample)), :, 2:]

    def get_raw_data(self) -> np.ndarray:
        return self.__data.reshape(self.__data.shape[0] * self.__data.shape[1], self.__data.shape[2])

    def rowCount(self) -> int:
        return len(self.__samples)
    
    def colCount(self) -> int:
        return len(self.__steps)
