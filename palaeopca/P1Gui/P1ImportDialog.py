import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QDialogButtonBox, QTableView, QGroupBox, QSpinBox, QComboBox, QCheckBox, QMessageBox

from palaeopca.P1Gui.P1PathPicker import P1PathPicker
from palaeopca.P1Backend.P1DataObject import P1DataObject
from palaeopca.P1Gui.P1DataModel import P1DataModel

class P1ImportDialog(QDialog):
    delimiters = {
        ",": ",",
        "{Space}": "\s+",
        "{Tab}": "\t",
        "|": "|",
        ":": ":",
        ";": ";",
    }

    def __init__(self, parent = None):
        super(P1ImportDialog, self).__init__(parent)
        self.setWindowTitle("Import data file")

        # TODO
        # Add Excel support
        #self.__filter = "All Files (*);;Excel files (*.xls *.xlsx);;CSV files (*.csv);;Text files (*.txt)"
        self.__filter = "All Files (*);;CSV files (*.csv);;Text files (*.txt)"

        if "xlsxwriter" in sys.modules:
            self.__filter += ";;Excel files (*.xls *.xlsx)"

        self.__setupGui()
        self.__connectGui()

        self.resize(QSize(650, 650))

    def __setupGui(self):
        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Filename:")
        self.pathPicker = P1PathPicker("file", self.__filter, "Choose data file to open")

        self.prevLabel = QLabel("File preview:")
        self.prevTable = QTableView()

        # Behaviour box widgets
        self.behaviourBox = QGroupBox("Behaviour")
        self.__behaviourLayout = QGridLayout(self.behaviourBox)

        self.skipHeaderLabel = QLabel("Skip top rows")
        self.skipHeaderSpin = QSpinBox()
        self.skipHeaderSpin.setMinimum(0)
        self.skipHeaderSpin.setValue(1)

        self.skipFooterLabel = QLabel("Skip bottom rows")
        self.skipFooterSpin = QSpinBox()
        self.skipFooterSpin.setMinimum(0)

        self.__behaviourLayout.addWidget(self.skipHeaderLabel, 0, 0)
        self.__behaviourLayout.addWidget(self.skipFooterLabel, 1, 0)

        self.__behaviourLayout.addWidget(self.skipHeaderSpin, 0, 1)
        self.__behaviourLayout.addWidget(self.skipFooterSpin, 1, 1)

        # Locale box widgets
        self.localeBox = QGroupBox("Locale")
        self.__localLayout = QGridLayout(self.localeBox)

        self.numericsLabel = QLabel("Numerics")
        self.numericsCombo = QComboBox()
        self.numericsCombo.addItems([".", ","])

        self.unitsLabel = QLabel("Units")
        self.unitsCombo = QComboBox()
        self.unitsCombo.addItems(["emu", "emu/cc", "Am2", "A/m"])

        self.__localLayout.addWidget(self.numericsLabel, 0, 0)
        self.__localLayout.addWidget(self.numericsCombo, 0, 1)
        self.__localLayout.addWidget(self.unitsLabel, 1, 0)
        self.__localLayout.addWidget(self.unitsCombo, 1, 1)

        # Delimiter box widgets
        self.delimiterBox = QGroupBox("Delimiter")
        self.__delimiterLayout = QGridLayout(self.delimiterBox)

        self.columnLabel = QLabel("Column")
        self.columnCombo = QComboBox()
        self.columnCombo.addItems([",", "{Space}", "{Tab}", "|", ":", ";"])

        self.skipSpaces = QCheckBox("Skip white spaces")

        self.__delimiterLayout.addWidget(self.columnLabel, 0, 0)
        self.__delimiterLayout.addWidget(self.skipSpaces, 1, 0, 1, 2)

        self.__delimiterLayout.addWidget(self.columnCombo, 0, 1)

        # Setup button box
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.pathPicker, 0, 1)
        
        self.__layout.addWidget(self.prevLabel, 1, 0, 1, 2)
        self.__layout.addWidget(self.prevTable, 2, 0, 1, 2)
        self.__layout.addWidget(self.behaviourBox, 3, 0, 2, 1)
        self.__layout.addWidget(self.localeBox, 3, 1)
        self.__layout.addWidget(self.delimiterBox, 4, 1)

        self.__layout.addWidget(self.buttonBox, 5, 0, 1, 2)

    def __connectGui(self):
        self.pathPicker.lineChanged.connect(self.__updateTable)

    def __updateTable(self, *args):
        # Get user input
        infile = self.pathPicker.getPath()
        if len(infile) == 0:
            return

        skip_header = self.skipHeaderSpin.value()
        skip_footer = self.skipFooterSpin.value()
        numerics = self.numericsCombo.currentText()
        sep = self.delimiters[self.columnCombo.currentText()]
        skip = self.skipSpaces.isChecked()
        units = self.unitsCombo.currentText()

        # Set data object and load data
        data = P1DataObject()
        try:
            data.load_data(infile, sep, skip_header)
        except UnicodeDecodeError:
            QMessageBox.warning(self, "Import warning", "Error while reading input file!", QMessageBox.Ok)
            return
        except IndexError:
            QMessageBox.warning(self, "Import warning", "Error while reading input file!", QMessageBox.Ok)
            return

        data.set_units(units)
        model = P1DataModel(data, ["SampleID/Depth", "Steps", "x", "y", "z"])

        self.prevTable.setModel(model)

        self.data = data
