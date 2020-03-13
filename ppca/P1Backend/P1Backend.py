# Import
import sys
from typing import Dict, List
import numpy as np

if "PyQt5" in sys.modules:
    from PyQt5.QtWidgets import QApplication

from ppca.P1Backend.P1DataObject import P1DataObject


class P1Backend(object):
    def __init__(self):
        self.__data = P1DataObject()

    def load_file(self, infile: str, sep: str, skip_header: int = 0, volume: float = 10.0, units: str = "emu"):
        """
        Loads a datafile of known format.

        Keywords:
            infile: full path to file (str)
            sep: file delimiter (str)
            skip_header: header lines to skip (int)
            volume: sample volume in g/cc (float, default: 10.0)
            units_in: units of input data (str, default: emu)
            units_out: convert units to units_out (str, default: Am2)

        Format:
            Columns: SampleID/Depth, AF (mT)/Temp. (K or °C), x (emu or Am2), y (emu or Am2), z (emu or Am2)
            Rows: Observations

            File may contain several samples, order first by sample, second by AF in ascending order.
            All samples need to have the same number of AF steps
        """
        self.__data.load_data(infile, sep, skip_header)
        self.__data.set_volume(volume)
        self.__data.set_units(units)

    def set_data(self, indata: P1DataObject):
        self.__data = indata

    def get_data(self) -> P1DataObject:
        """
        Returns the underlying data object
        """
        return self.__data

    def run_single_interval(self, min_step: float = 0.0, max_step: float = 100.0, NRM_unit: str = "A/m", pbar = None) -> np.ndarray:
        """
        Run a principal component analysis (PCA) on the data in the given interval.

        Keywords:
            min_step: first step to be used, in step units (e.g., mT)
            max_step: last step to be used, in step units (e.g., mT)
            NRM_unit: units for NRM (str, default = A/m)
        
        Returns:
            numpy array (SampleID/Depth, NRM, Inclination, Declination, MADp, MADo, Min step, Max step)
        """

        # Prepare output
        outdata = np.zeros((self.__data.rowCount(), 8))
        outdata[:, 0] = self.__data.get_samples()

        # Loop through unique samples in data
        pbar_steps = 100 / self.__data.rowCount()
        new_value = 0
        for n, sample in enumerate(self.__data.get_samples()):
            # Get corresponding sample data
            A = self.__data.get_data(sample)

            # Calculate, convert and save NRM convert to provided unit
            NRM = np.sqrt(A[0, 0]**2 + A[0, 1]**2 + A[0, 2]**2) * self.get_conversion_factor(self.__data.get_units(), NRM_unit)
            outdata[n, 1] = NRM

            # Save data that will be used for PCA
            B = A[np.where(np.logical_and(self.__data.get_steps() >= min_step, self.__data.get_steps() <= max_step)), :][0]
            
            # Run PCA and save results
            results = self.ppca(B)

            outdata[n, 2] = results["Inclination"]
            outdata[n, 3] = results["Declination"]
            outdata[n, 4] = results["MADp"]
            outdata[n, 5] = results["MADo"]
            outdata[n, 6] = min_step
            outdata[n, 7] = max_step

            if pbar != None:
                new_value += pbar_steps
                if int(new_value) > pbar.progress.value():
                    pbar.progress.setValue(int(new_value))
                QApplication.processEvents()

        return outdata

    def run_best_fit(self, min_steps: int = 3, NRM_unit: str = "A/m", pbar = None) -> np.ndarray:
        """
        Run a principal component analysis (PCA) on the data minimizing the MADp.

        Keywords:
            min_steps: minimum number of steps to be used (int, default: 3)
            NRM_unit: units for NRM (str, default = A/m)
        
        Returns:
            numpy array (SampleID/Depth, NRM, Inclination, Declination, MADp, MADo, Min step, Max step)
        """
        # Need at least 3 steps, set to 3 if less
        if min_steps < 3:
            min_steps = 3

        # Prepare output
        outdata = np.zeros((self.__data.rowCount(), 8))
        outdata[:, 0] = self.__data.get_samples()

        # Loop through unique samples in data
        pbar_steps = 100 / self.__data.rowCount()
        new_value = 0
        for n, sample in enumerate(self.__data.get_samples()):
            # Get corresponding sample data
            A = self.__data.get_data(sample)

             # Calculate, convert and save NRM convert to provided unit
            NRM = np.sqrt(A[0, 0]**2 + A[0, 1]**2 + A[0, 2]**2) * self.get_conversion_factor(self.__data.get_units(), NRM_unit)
            outdata[n, 1] = NRM

            # Set an abritraty MADp
            outdata[n, 4] = 10*5

            # Iterate through array
            window = min_steps
            while window <= len(self.__data.get_steps()):
                for index_0 in range(len(self.__data.get_steps()[:-window+1])):
                    B = A[index_0:index_0 + window, :]
                    results = self.ppca(B)
                    if results["MADp"] < outdata[n, 4]:
                        outdata[n, 2] = results["Inclination"]
                        outdata[n, 3] = results["Declination"]
                        outdata[n, 4] = results["MADp"]
                        outdata[n, 5] = results["MADo"]
                        outdata[n, 6] = self.__data.get_steps()[index_0]
                        outdata[n, 7] = self.__data.get_steps()[index_0 + window - 1]
                # Increase window by 1
                window += 1

            if pbar != None:
                new_value += pbar_steps
                if int(new_value) > pbar.progress.value():
                    pbar.progress.setValue(int(new_value))
                QApplication.processEvents()

        return outdata

    def run_mesh(self, window = 3, pbar = None) -> Dict:
        """
        Run a moving window principal component analysis (PCA) on the dat.

        Keywords:
            window: length of the moving window (int, default: 3)
        
        Returns:
            Dictionary with the numpy arrays of the following parameters:
                Samples: vector of SampleID/Depth.
                Centers: vector of window centers.
                Steps: vector of all steps.
                M: Magnetization matrix with observations in rows, windows in columns.
                Inclination: Inclination matrix with observations in rows, windows in columns.
                Declination: Declination matrix with observations in rows, windows in columns.
                MADp: medium angular deviation, prolate matrix with observations in rows, windows in columns.
                MADo: medium angular deviation, oblate matrix with observations in rows, windows in columns.
        """
        # Need at least 3 steps, set to 3 if less
        if window < 3:
            window = 3

        # Prepare output
        N = self.__data.colCount() - (window - 1) # Calculates number of columns
        outdata = {
            "Samples": self.__data.get_samples(),
            "Centers": np.zeros(N),
            "Steps": self.__data.get_steps(),
            "M": np.zeros((self.__data.rowCount(), self.__data.colCount())),
            "Inclination": np.zeros((self.__data.rowCount(), N)),
            "Declination": np.zeros((self.__data.rowCount(), N)),
            "MADp": np.zeros((self.__data.rowCount(), N)),
            "MADo": np.zeros((self.__data.rowCount(), N)),
        }

        # Loop through unique samples in data
        pbar_steps = 100 / self.__data.rowCount()
        new_value = 0
        for n, sample in enumerate(self.__data.get_samples()):
            # Get corresponding sample data
            A = self.__data.get_data(sample)

             # Calculate, convert and save NRM convert to provided unit
            for m in range(self.__data.colCount()):
                outdata["M"][n, m] = np.sqrt(A[m, 0]**2 + A[m, 1]**2 + A[m, 2]**2)

            # Iterate through array
            for index_0 in range(self.__data.colCount() - window + 1):
                if n == 0:
                    # Calculate and save window center
                    outdata["Centers"][index_0] = self.__data.get_steps()[index_0:index_0 + window].mean()
                
                B = A[index_0:index_0 + window, :]
                results = self.ppca(B)
                outdata["Inclination"][n, index_0] = results["Inclination"]
                outdata["Declination"][n, index_0] = results["Declination"]
                outdata["MADp"][n, index_0] = results["MADp"]
                outdata["MADo"][n, index_0] = results["MADo"]
            
            if pbar != None:
                new_value += pbar_steps
                if int(new_value) > pbar.progress.value():
                    pbar.progress.setValue(int(new_value))
                QApplication.processEvents()

        # Normalize NRM
        outdata["M"] = outdata["M"] / outdata["M"].max(axis = 1)[:, None]

        return outdata

    def get_conversion_factor(self, units_in: str, units_out: str) -> float:
        if units_in == "emu" and units_out == "Am2":
            return 10**(-3)
        elif units_in == "emu" and units_out == "A/m":
            return 10**(3) / self.__data.get_volume()
        elif units_in == "Am2" and units_out == "emu":
            return 10**(3)
        elif units_in == "Am2" and units_out == "A/m":
            return 10**6 / self.__data.get_volume()
        elif units_in == "A/m" and units_out == "emu":
            return self.__data.get_volume() * 10**(-3)
        else:
            return 1
        
    def center(self, A: np.ndarray) -> np.ndarray:
        """
        Function to center data according to zi = (xi - X)

        Keyword arguments:
            A: data matrix with variables (x, y, z) in columns and observations in rows

        Returns:
            centered data matrix
        """
        return A - A.mean(axis = 0)

    def ppca(self, indata: np.ndarray, anchor: bool = False, vec = 0) -> Dict:
        """
        Function to perform a principal component analysis (PCA) on set of (x, y, z) vectors by singular value decomposition (SVD)

        Keyword arguments:
        indata: data matrix with variables (x, y, z) in columns and observations in rows
        anchor: true = use unmodified data, false (default) = mean center data
        vec: eigenvector to return results from (default: 0 [largest])

        Returns:
            Dictionary with the following parameters:
                Inclination: Inclination.
                Declination: Declination.
                MADp: medium angular deviation, prolate.
                MADo: medium angular deviation, oblate.
                Evals: Vector of singular values in decending order, corresponds to Eigenvalues of data covariance matrix.
                Evecs: Matrix of right singular vectors, corresponds to Eigenvectors of data covariance matrix.
                Variance_Explained: percentage of variance explained by the individual components.
        """

        # Mean center
        if anchor: M = indata
        else: M = self.center(indata)
        
        # Calculate covariance matrix
        B = np.cov(M.T)

        # SVD
        # Returns empty results dictionary when svd does not converge
        try:
            [U, evals, evecs] = np.linalg.svd(B)
        except np.linalg.LinAlgError:
            results = {
                "Inclination": np.nan,
                "Declination": np.nan,
                "MADp": np.nan,
                "MADo": np.nan,
                "Evals": np.array([np.nan, np.nan, np.nan]),
                "Evecs": np.array([[np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan]]),
                "Variance_Explained": np.array([[np.nan, np.nan, np.nan]])
            }

            return results
        
        # Calculate scores
        scores = U * evals

        # Sort and transpose eigenvectors
        evecs = evecs.T

        # Save largest eigenvector
        #e1 = evecs[:,2]

        # Determine direction
        first = M[0]
        last = M[-1:]
        trend = last - first

        # When two vectors generally point in the same direction, their dot product is positive
        # When they are perpendicular, their dot product is zero
        # When they point in opposing directions, their dot procut is negative
        
        if trend.dot(evecs[:, 0]) > 0:
            evecs[:, 0] *= -1
        if trend.dot(evecs[:, 1]) > 0:
            evecs[:, 1] *= -1
        if trend.dot(evecs[:, 2]) > 0:
            evecs[:, 2] *= -1
        
        # Calculate ChRM
        Incl = []
        Decl = []
        for column in range(evecs.shape[1]):
            pca_x = evecs[0, column]
            pca_y = evecs[1, column]
            pca_z = evecs[2, column]
                
            # Inclination
            pca_inc_1 = np.sqrt(pca_x**2 + pca_y**2)
            pca_inc_2 = pca_z

            Incl.append(np.degrees(np.arctan2(pca_inc_2, pca_inc_1)))

            # Declination
            Decl.append(180 + np.degrees(np.arctan2(pca_y, pca_x)))

        # MAD
        MADp = np.degrees(np.arctan(np.sqrt((evals[2] + evals[1])/evals[0])))
        MADo = np.degrees(np.arctan(np.sqrt(evals[2]/(evals[1] + evals[0]))))

        results = {
            "Declination": Decl[vec],
            "Inclination": Incl[vec],
            "MADp": MADp,
            "MADo": MADo,
            "Evals": evals,
            "Evecs": evecs,
            "Variance_Explained": scores.std(axis = 1)**2 / np.sum(scores.std(axis = 1)**2)
        }

        return results
