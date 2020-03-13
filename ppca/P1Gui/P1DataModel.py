from typing import List

from PyQt5.QtCore import Qt, QAbstractTableModel
from ppca.P1Backend.P1DataObject import P1DataObject

class P1DataModel(QAbstractTableModel):
    def __init__(self, data: P1DataObject, header: List, parent = None):
        QAbstractTableModel.__init__(self, parent)
        self._dataObject = data
        self._data = data.get_raw_data()
        self._header = header

    def rowCount(self, parent = None):
        return self._data.shape[0]

    def columnCount(self, parent = None):
        return self._data.shape[1]

    def data(self, index, role = Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header[col]
        return None