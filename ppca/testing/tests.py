import numpy as np

A = np.asarray([0.5, 1, 2, 3, 4])

print(A)
print(str(A))
print(",".join([str(x) for x in A]))

import sys
import xlsxwriter

for key in sys.modules:
    print(key)