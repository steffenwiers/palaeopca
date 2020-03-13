# Imports
from typing import Tuple
import numpy as np


# Functions
def convert_to_xyz(Inc: float, Dec: float, Int: float) -> Tuple:
    """
    Converts Inclination, Declination, Intensity vector to x, y, z vector

    Keyword arguments:
        Inc: Inclination in degree
        Dec: Declination in degree
        Int: Intensity in any valid unit (return units will be in the same unit as the input)

    Returns:
        (x, y, z): Tuple with x, y & z values
    """
    Inc = np.radians(Inc)
    Dec = np.radians(Dec)
    x = Int * np.cos(Inc) * np.cos(Dec)
    y = Int * np.cos(Inc) * np.sin(Dec)
    z = Int * np.sin(Inc)

    return (x, y, z)

assert convert_to_xyz(45, 45, 45) == (22.500000000000004, 22.5, 31.819805153394636)