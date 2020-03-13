# ppca
A python tool to perform principal component (PCA) analysis on palaeomagnetic data sets.

## Main features
PPCA tools provides three convinient functions for PCA of palaeomagnetic sequence data, such as continues data from marine sediment cores. The underlying functionallity can be used without the gui by importing P1Backend directly into your code. The backend provides:
 - Single interval PCA to analyse all samples in a given interval
 - Best fit PCA to find the lowest possible medium angular deviation (MAD) for each sample
 - Mesh PCA to run a moving window PCA

The user interface makes it possible to run ppca without any knowledge of the python programming language. It allows for data import, display and analysis and well as export of the results as comma separated files, Excel files and images.

## Installation
### Manual
To install ppca manually you need a running version of python 3 and at least NumPy and Matplotlib. For gui support you also need PyQt5 and for Excel file integration you need xlsxwriter. Step-by-step instructions:
 1. Clone the repository.
 2. Open a command promt (Windows) or a terminal window (Unix) and navigate to the root folder of ppca (the one that contains setup.py).
 3. Create a python virtual environment by running:

    ```python -m venv ppca_venv```
 4. Activate the virtual environment

    Windows: ```source ./venv/Scripts/activate```
    Unix: ```source ./venv/bin/activate```
 5. Install required dependencies into the virtual environment

    ```pip install numpy matplotlib```
 6. Install optional dependencies  into the virtual environment (optional)

    ```pip install PyQt5 xlsxwriter```
 7. Install the ppca package into the virtual environment

    ```pip install -e .```

### PyPI
To install ppca via pip simply run the following commands:

```pip install ppca numpy matplotlib```

```pip install PyQt5 xlsxwriter``` (optional)