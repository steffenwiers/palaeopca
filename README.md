# ppca
Tool to perform principal component (PCA) analysis on palaeomagnetic data sets.

## Main features

PPCA tools provides three convinient functions for PCA of palaeomagnetic sequence data, such as continues data from marine sediment cores. The underlying functionallity can be used without the gui by importing P1Backend directly into your code. The backend provides:
 - Single interval PCA to analyse all samples in a given interval
 - Best fit PCA to find the lowest possible medium angular deviation (MAD) for each sample
 - Mesh PCA to run a moving window PCA
