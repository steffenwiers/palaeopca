# Imports
import numpy as np


class P1DataObject(object):
    """
    Container class for 3-dimensional vector data.
    """
    def __init__(self):
        """
        Initializes empty containers and default values.
        """
        self.__data = None
        self.__samples = None
        self.__steps = None
        self.__volume = 10
        self.__units = "emu"

    def load_data(self, infile: str, sep: str, skip_header: int=0):
        """
        Loads a data file.

        :type infile: string
        :type sep: string
        :type skip_header: integer

        :param infile: full path to input file
        :param sep: file delimiter
        :param skip_header: header lines to skip
        """
        # Try to read the first line as the header
        if skip_header > 0:
            with open(infile, 'r') as fin:
                header = fin.readline()
            fin.close()
            self.__header = header.split(sep)
        else:
            self.__header = []

        data = np.genfromtxt(infile, delimiter = sep, skip_header = skip_header)
        data = data.reshape(len(np.unique(data[:, 0])), len(np.unique(data[:, 1])), data.shape[1])

        self.__data = data
        self.__samples = data[:, 0, 0]
        self.__steps = data[0, :, 1]

    def set_volume(self, volume: float=10.0):
        """
        Set sample volume.

        :type volume: float
        :param volume: sample volume in g/cc
        """
        self.__volume = volume

    def set_units(self, units: str):
        """
        Set input data units

        :type units: string
        :param units: input units (emu, Am2, A/m)
        """
        self.__units = units

    def set_header(self, new_header: list):
        """
        Set data header

        :type new_header: list
        :param new_header: list of header labels, must be of length (5)
        """
        self.__header = new_header

    def get_units(self):
        """
        Returns data units
        """
        return self.__units

    def get_header(self) -> list:
        return self.__header

    def get_volume(self):
        """
        Returns sample volume
        """
        return self.__volume
        
    def get_steps(self) -> np.ndarray:
        """
        Returns demagnetization steps

        :returns: list of all AF/Temp steps
        :rtype: numpy.ndarray
        """
        return self.__steps

    def get_samples(self) -> np.ndarray:
        """
        Returns a list of all samples

        :returns: sample list
        :rtype: numpy.ndarray
        """
        return self.__samples

    def get_data(self, sample) -> np.ndarray:
        """
        Returns data for specified sample

        :type sample: string or integer or float
        :param sample: sample id

        :returns: array with data
        :rtype: numpy.ndarray
        """
        samples = [str(x) for x in self.get_samples()]
        return self.__data[samples.index(str(sample)), :, 2:]

    def get_raw_data(self) -> np.ndarray:
        """
        Returns the unsctructured raw data as was read from the input file

        :returns: raw data
        :rtype: numpy.ndarray
        """
        return self.__data.reshape(self.__data.shape[0] * self.__data.shape[1], self.__data.shape[2])

    def rowCount(self) -> int:
        """
        Returns sample count

        :returns: number of samples
        :rtype: integer
        """
        return len(self.__samples)
    
    def colCount(self) -> int:
        """
        Returns AF/Temp step count

        :returns: number of steps
        :rtype: integer
        """
        return len(self.__steps)
