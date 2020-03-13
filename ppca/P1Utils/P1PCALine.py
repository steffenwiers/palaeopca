# Imports
from typing import List
import numpy as np

def PCALine(x, y, r, stdv = 1) -> (List, List):
    """
    Function to calculate points for PCA fit

    Keywords:
        x: x data points
        y: y data points
        r: angle in radians
        stdv: scaling factor in standard deviations (default: 1)

    Returns:
        Tuple with (x1, x2), (y1, y2) coordinates
    """
    x_pca = x.mean()
    y_pca = y.mean()

    dx = np.sin(r)
    dy = np.cos(r)

    x_line = [(x_pca - dx), (x_pca + dx)]
    y_line = [(y_pca - dy), (y_pca + dy)]

    slope = (y_line[1] - y_line[0]) / (x_line[1] - x_line[0])
    intercept = y_line[0] - slope * x_line[0]

    x_points = np.asarray([x.min() - stdv * x.std(), x.max() + stdv * x.std()])
    y_points = slope * x_points + intercept

    return x_points, y_points