palaeopca.P1Backend.P1DataObject module
=======================================

.. automodule:: palaeopca.P1Backend.P1DataObject
   :members:
   :undoc-members:
   :show-inheritance:

Examples
--------
>>> from io import StringIO
>>> from palaeopca.P1Backend.P1DataObject import P1DataObject
>>> infile = StringIO(u"1,0,1,1,1\n1,50,0.5,0.5,0.5\n2,0,2,2,2\n2,50,1,1,1")
>>> data = P1DataObject()
>>> data.load_data(infile, sep=",")
>>> data.get_samples()
[1., 2.]
>>> data.get_data(1.)
array([[2., 2., 2.],
       [1., 1., 1.]])