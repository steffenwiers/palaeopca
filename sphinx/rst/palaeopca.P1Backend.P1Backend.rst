palaeopca.P1Backend.P1Backend module
====================================

.. automodule:: palaeopca.P1Backend.P1Backend
   :members:
   :undoc-members:
   :show-inheritance:

Examples
--------
Single interval

>>> from io import StringIO
>>> from palaeopca.P1Backend.P1Backend import P1Backend
>>> infile = StringIO(u"1,0,1,1,1\n1,50,0.5,0.5,0.5\n2,0,2,2,2\n2,50,1,1,1")
>>> p = P1Backend()
>>> p.load_file(infile, sep=",")
>>> p.run_single_interval()
array([[  1.        , 173.20508076,  35.26438968, 225.        ,
          0.        ,   0.        ,   0.        , 100.        ],
       [  2.        , 346.41016151,  35.26438968, 225.        ,
          0.        ,   0.        ,   0.        , 100.        ]])