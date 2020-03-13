# Imports
import numpy as np


# Functions
def load_file(infile: str) -> np.ndarray:
    """
    Loads a data file of known format:
        Columns: AF (mT), x (emu or Am2), y (emu or Am2), z (emu or Am2)
        Rows: Observations

        File may contain several samples, order first by sample, second by AF in ascending order

    Returns:
        Data matrix
    """
    try:
        return np.genfromtxt(infile, delimiter = ",", skip_header = 1)
    except FileNotFoundError:
        raise FileNotFoundError

def save_file(outfile: str, sample: np.ndarray, nrm: np.ndarray, inc: np.ndarray, dec: np.ndarray, madp: np.ndarray, mado: np.ndarray) -> np.ndarray:
    """
    Saves pca results
    """
    outdata = np.asarray([
        sample,
        nrm,
        inc,
        dec,
        madp,
        mado,
    ]).T

    np.savetxt(outfile, outdata, delimiter = ",", header = "Sample,NRM,Inclination,Declination,MADp,MADo")

    return outdata