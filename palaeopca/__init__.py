import os

__author__ = "Steffen Wiers"
__copyright__ = "Copyright 2020 Steffen Wiers"
__license__ = "MIT License"
__maintainer__ = __author__
__email__ = "steffen.p.wiers@gmail.com"
__version_info__ = (1, 0, 2)
__version__ = '.'.join(str(e) for e in __version_info__)
__description__ = "Tool to perform principal component analysis on palaeomagnetic data sets."

basedir = os.path.dirname(os.path.realpath(__file__))
basedir = basedir.replace("\\", "/")
