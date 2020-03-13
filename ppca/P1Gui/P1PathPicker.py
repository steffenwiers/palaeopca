from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton, QFileDialog

import ppca.P1Utils.P1PixmapCache


class P1PathPicker(QWidget):
    """
    Class implementing a small vboxlayout with a line edit and a browse button
    """
    lineChanged = pyqtSignal()

    def __init__(self, typ="file", fil = None, sFil = None, text = None, parent = None):
        """
        Constructor

        :param parent: parent Widget (QWidget)
        """
        super(P1PathPicker, self).__init__(parent)

        self.type = typ
        self.filter = fil
        self.sFilter = sFil
        self.text = text

        self.__layout = QHBoxLayout(self)
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.__layout)

        self.__lineEdit = QLineEdit()

        self.__button = QToolButton(self)
        self.__button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.__button.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("folder-open", "solid"))

        self.__button.clicked.connect(self.__showPathPickerDialog)

        self.__layout.addWidget(self.__lineEdit)
        self.__layout.addWidget(self.__button)

    def __showPathPickerDialog(self):
        """
        Private method to call a browse dialog to pick a path.
        """
        dialog = QFileDialog()
        if self.type == "file":
            path = dialog.getOpenFileName(None, self.text, "", self.filter, self.sFilter)[0]
        elif self.type == "dir":
            path = dialog.getExistingDirectory(None, self.text)
        elif self.type == "save":
            path = dialog.getSaveFileName(None, self.text, "", self.filter, self.sFilter)[0]

        self.__lineEdit.setText(path)
        self.lineChanged.emit()

    def getPath(self):
        """
        Public method to return the current path.
        """
        return self.__lineEdit.text()

    def setPath(self, path):
        """
        Public method to set the path.
        :param path: path (str)
        """
        self.__lineEdit.setText(path)
