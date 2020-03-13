# Standard library
import sys
from ast import literal_eval

# Qt
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtWidgets import QDialog, \
    QGridLayout, \
    QVBoxLayout, \
    QHBoxLayout, \
    QGroupBox, \
    QLabel, \
    QComboBox, \
    QLineEdit, \
    QCheckBox, \
    QDialogButtonBox

# Matplotlib
import matplotlib.pyplot as plt

# ppca
from ppca.P1Gui.P1PathPicker import P1PathPicker


class P1ZijderExport(QDialog):
    def __init__(self, parent = None):
        super(P1ZijderExport, self).__init__(parent)
        self.setWindowTitle("Export Zijderveld plots")
        self.__setupGui()

    def __setupGui(self):
        s = QSettings()

        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Output directory:")
        self.pathPicker = P1PathPicker("dir", "", "Choose output directory")

        # Figure box widgets
        self.paramBox = QGroupBox("Figure")
        self.__paramLayout = QGridLayout(self.paramBox)

        self.__formatLabel = QLabel("File format")
        self.formatCombo = QComboBox()
        formats = [key for key in plt.gcf().canvas.get_supported_filetypes()]
        self.formatCombo.addItems(formats)
        self.formatCombo.setCurrentText(s.value("Zijder/fmt", "png"))

        size = literal_eval(s.value("Zijder/Size", "(5, 5)"))
        self.__figureWLabel = QLabel("Figure width (in)")
        self.figure_width = QLineEdit(str(size[0]))

        self.__figureHLabel = QLabel("Figure height (in)")
        self.figure_height = QLineEdit(str(size[1]))

        self.__figureDPILabel = QLabel("Figure dpi")
        self.figure_dpi = QLineEdit(str(s.value("Zijder/dpi", "300")))

        self.__paramLayout.addWidget(self.__formatLabel, 0, 0)
        self.__paramLayout.addWidget(self.formatCombo, 0, 1)

        self.__paramLayout.addWidget(self.__figureWLabel, 0, 2)
        self.__paramLayout.addWidget(self.figure_width, 0, 3)

        self.__paramLayout.addWidget(self.__figureDPILabel, 1, 0)
        self.__paramLayout.addWidget(self.figure_dpi, 1, 1)

        self.__paramLayout.addWidget(self.__figureHLabel, 1, 2)
        self.__paramLayout.addWidget(self.figure_height, 1, 3)

        # Directions box widgets
        self.dirBox = QGroupBox("Directions")
        self.__dirLayout = QGridLayout(self.dirBox)

        self.__xhLabel = QLabel("Horizontal x")
        self.__xvLabel = QLabel("Vertical x")
        self.__yLabel = QLabel("Horizontal y")
        self.__zLabel = QLabel("Vertical y")

        self.xhCombo = QComboBox()
        self.xhCombo.addItems(["N", "S", "E", "W"])
        self.xhCombo.setCurrentText(s.value("Zijder/xh", "N"))

        self.xvCombo = QComboBox()
        self.xvCombo.addItems(["N", "S", "E", "W"])
        self.xvCombo.setCurrentText(s.value("Zijder/xv", "N"))

        self.yCombo = QComboBox()
        self.yCombo.addItems(["N", "S", "E", "W"])
        self.yCombo.setCurrentText(s.value("Zijder/y", "W"))

        self.zCombo = QComboBox()
        self.zCombo.addItems(["Up", "Down"])
        self.zCombo.setCurrentText(s.value("Zijder/z", "Up"))

        self.__dirLayout.addWidget(self.__xhLabel, 0, 0)
        self.__dirLayout.addWidget(self.xhCombo, 0, 1)
        self.__dirLayout.addWidget(self.__yLabel, 0, 2)
        self.__dirLayout.addWidget(self.yCombo, 0, 3)

        self.__dirLayout.addWidget(self.__xvLabel, 1, 0)
        self.__dirLayout.addWidget(self.xvCombo, 1, 1)
        self.__dirLayout.addWidget(self.__zLabel, 1, 2)
        self.__dirLayout.addWidget(self.zCombo, 1, 3)

        # PCA box widgets
        self.PCABox = QGroupBox("PCA Results")
        self.__pcaLayout = QVBoxLayout(self.PCABox)

        self.markCheck = QCheckBox("Mark steps used in PCA")
        self.annoCheck = QCheckBox("Add PCA results to legend")
        self.lineCheck = QCheckBox("Plot PCA lines")

        self.markCheck.setChecked(literal_eval(s.value("Zijder/mark", "False")))
        self.annoCheck.setChecked(literal_eval(s.value("Zijder/anno", "False")))
        self.lineCheck.setChecked(literal_eval(s.value("Zijder/line", "False")))

        self.__pcaLayout.addWidget(self.markCheck)
        self.__pcaLayout.addWidget(self.annoCheck)
        self.__pcaLayout.addWidget(self.lineCheck)

        # Setup button box
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.pathPicker, 0, 1)
        
        self.__layout.addWidget(self.paramBox, 1, 0, 1, 2)
        self.__layout.addWidget(self.dirBox, 2, 0, 1, 2)
        self.__layout.addWidget(self.PCABox, 3, 0, 1, 2)

        self.__layout.addWidget(self.buttonBox, 4, 0, 1, 2)

class P1SequenceExport(QDialog):
    def __init__(self, parent = None):
        super(P1SequenceExport, self).__init__(parent)
        self.setWindowTitle("Export Sequence plot")
        self.__setupGui()

    def __setupGui(self):
        s = QSettings()

        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Output file:")
        __fmt = plt.gcf().canvas.get_supported_filetypes()
        __filter = ["{0} (*.{1})".format(__fmt[key], key) for key in __fmt]
        __filter = ";;".join(__filter)
        __sFilter = "{0} (*.{1})".format(__fmt[s.value("Sequence/fmt")], s.value("Sequence/fmt"))
        self.pathPicker = P1PathPicker("save", __filter, __sFilter, "Choose output file")

        # Figure box widgets
        self.figureBox = QGroupBox("Figure")
        self.__figureLayout = QGridLayout(self.figureBox)

        size = literal_eval(s.value("Sequence/Size", "(5, 5)"))
        self.__figureWLabel = QLabel("Figure width (in)")
        self.figure_width = QLineEdit(str(size[0]))

        self.__figureHLabel = QLabel("Figure height (in)")
        self.figure_height = QLineEdit(str(size[1]))

        self.__figureDPILabel = QLabel("Figure dpi")
        self.figure_dpi = QLineEdit(str(s.value("Sequence/dpi", "300")))

        self.__figureLayout.addWidget(self.__figureWLabel, 0, 0)
        self.__figureLayout.addWidget(self.figure_width, 0, 1)

        self.__figureLayout.addWidget(self.__figureDPILabel, 0, 2)
        self.__figureLayout.addWidget(self.figure_dpi, 0, 3)

        self.__figureLayout.addWidget(self.__figureHLabel, 1, 0)
        self.__figureLayout.addWidget(self.figure_height, 1, 1)

        # Parameter box widgets
        self.paramBox = QGroupBox("Parameters")
        self.__paramLayout = QGridLayout(self.paramBox)

        self.nrmCheck = QCheckBox("NRM")
        self.incCheck = QCheckBox("Inclination")
        self.decCheck = QCheckBox("Declination")
        self.madpCheck = QCheckBox("MADp")
        self.madoCheck = QCheckBox("MADo")
        self.invCheck = QCheckBox("Invert Y")

        self.nrmCheck.setChecked(literal_eval(s.value("Sequence/NRM", "True")))
        self.incCheck.setChecked(literal_eval(s.value("Sequence/Incl", "True")))
        self.decCheck.setChecked(literal_eval(s.value("Sequence/Decl", "True")))
        self.madpCheck.setChecked(literal_eval(s.value("Sequence/MADp", "True")))
        self.madoCheck.setChecked(literal_eval(s.value("Sequence/MADo", "True")))
        self.invCheck.setChecked(literal_eval(s.value("Sequence/invertY", "True")))

        self.__paramLayout.addWidget(self.nrmCheck, 0, 0)
        self.__paramLayout.addWidget(self.incCheck, 0, 1)
        self.__paramLayout.addWidget(self.decCheck, 1, 0)
        self.__paramLayout.addWidget(self.madpCheck, 1, 1)
        self.__paramLayout.addWidget(self.madoCheck, 2, 0)
        self.__paramLayout.addWidget(self.invCheck, 2, 1)

        # Label box
        self.labelBox = QGroupBox("Labels")
        self.__labelLayout = QGridLayout(self.labelBox)

        self.__nrmLabel = QLabel("NRM unit")
        self.__yLabel = QLabel("y-Axis label")

        self.nrmLine = QLineEdit(s.value("Units/output", "A/m"))
        self.yLine = QLineEdit("Depth/SampleID")

        self.__labelLayout.addWidget(self.__nrmLabel, 0, 0)
        self.__labelLayout.addWidget(self.__yLabel, 1, 0)
        self.__labelLayout.addWidget(self.nrmLine, 0, 1)
        self.__labelLayout.addWidget(self.yLine, 1, 1)

        # Setup button box
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.pathPicker, 0, 1)
        
        self.__layout.addWidget(self.figureBox, 1, 0, 1, 2)
        self.__layout.addWidget(self.paramBox, 2, 0, 1, 2)
        self.__layout.addWidget(self.labelBox, 3, 0, 1, 2)

        self.__layout.addWidget(self.buttonBox, 4, 0, 1, 2)

class P1MeshExport(QDialog):
    def __init__(self, parent = None):
        super(P1MeshExport, self).__init__(parent)
        self.setWindowTitle("Export Mesh plot")
        self.__setupGui()

    def __setupGui(self):
        s = QSettings()

        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Output file:")
        __filter = ["{0} file (*.{0})".format(key) for key in plt.gcf().canvas.get_supported_filetypes()]
        __filter = ";;".join(__filter)
        __filter = "(" + __filter + ")"
        self.pathPicker = P1PathPicker("save", __filter, "Choose output file")

        # Figure box widgets
        self.paramBox = QGroupBox("Figure")
        self.__paramLayout = QGridLayout(self.paramBox)

        size = literal_eval(s.value("Mesh/Size", "(5, 5)"))
        self.__figureWLabel = QLabel("Figure width")
        self.figure_width = QLineEdit(str(size[0]))

        self.__figureHLabel = QLabel("Figure height (in)")
        self.figure_height = QLineEdit(str(size[1]))

        self.__figureDPILabel = QLabel("Figure width (in)")
        self.figure_dpi = QLineEdit(str(s.value("Mesh/dpi", "300")))

        self.__paramLayout.addWidget(self.__figureWLabel, 0, 0)
        self.__paramLayout.addWidget(self.figure_width, 0, 1)

        self.__paramLayout.addWidget(self.__figureDPILabel, 0, 2)
        self.__paramLayout.addWidget(self.figure_dpi, 0, 3)

        self.__paramLayout.addWidget(self.__figureHLabel, 1, 0)
        self.__paramLayout.addWidget(self.figure_height, 1, 1)

        # Parameter box widgets
        self.paramBox = QGroupBox("Parameters")
        self.__paramLayout = QGridLayout(self.paramBox)

        self.nrmCheck = QCheckBox("NRM")
        self.incCheck = QCheckBox("Inclination")
        self.decCheck = QCheckBox("Declination")
        self.madpCheck = QCheckBox("MADp")
        self.madoCheck = QCheckBox("MADo")
        self.invCheck = QCheckBox("Invert Y")

        self.nrmCheck.setChecked(literal_eval(s.value("Mesh/NRM", "True")))
        self.incCheck.setChecked(literal_eval(s.value("Mesh/Incl", "True")))
        self.decCheck.setChecked(literal_eval(s.value("Mesh/Decl", "True")))
        self.madpCheck.setChecked(literal_eval(s.value("Mesh/MADp", "True")))
        self.madoCheck.setChecked(literal_eval(s.value("Mesh/MADo", "True")))
        self.invCheck.setChecked(literal_eval(s.value("Mesh/invertY", "True")))

        self.__paramLayout.addWidget(self.nrmCheck, 0, 0)
        self.__paramLayout.addWidget(self.incCheck, 0, 1)
        self.__paramLayout.addWidget(self.decCheck, 1, 0)
        self.__paramLayout.addWidget(self.madpCheck, 1, 1)
        self.__paramLayout.addWidget(self.madoCheck, 2, 0)
        self.__paramLayout.addWidget(self.invCheck, 2, 1)

        # Setup button box
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.pathPicker, 0, 1)
        
        self.__layout.addWidget(self.paramBox, 1, 0, 1, 2)
        self.__layout.addWidget(self.paramBox, 2, 0, 1, 2)

        self.__layout.addWidget(self.buttonBox, 3, 0, 1, 2)

class P1MeshDataExport(QDialog):
    def __init__(self, parent = None):
        super(P1MeshDataExport, self).__init__(parent)
        self.setWindowTitle("Export Mesh data")
        self.__setupGui()

    def __setupGui(self):
        s = QSettings()

        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Output directory:")
        self.pathPicker = P1PathPicker("dir", "", "Choose output directory")

        # Parameter box widget
        self.paramBox = QGroupBox("Parameters")
        self.__paramLayout = QGridLayout(self.paramBox)

        self.nrmCheck = QCheckBox("Magnetization")
        self.incCheck = QCheckBox("Inclination")
        self.decCheck = QCheckBox("Declination")
        self.madpCheck = QCheckBox("MADp")
        self.madoCheck = QCheckBox("MADo")

        self.nrmCheck.setChecked(literal_eval(s.value("Mesh/NRM", "True")))
        self.incCheck.setChecked(literal_eval(s.value("Mesh/Incl", "True")))
        self.decCheck.setChecked(literal_eval(s.value("Mesh/Decl", "True")))
        self.madpCheck.setChecked(literal_eval(s.value("Mesh/MADp", "True")))
        self.madoCheck.setChecked(literal_eval(s.value("Mesh/MADo", "True")))

        self.__paramLayout.addWidget(self.nrmCheck, 0, 0)
        self.__paramLayout.addWidget(self.incCheck, 0, 1)
        self.__paramLayout.addWidget(self.decCheck, 1, 0)
        self.__paramLayout.addWidget(self.madpCheck, 1, 1)
        self.__paramLayout.addWidget(self.madoCheck, 2, 0)

        # Vector box widget
        self.vecBox = QGroupBox("Vectors")
        self.__vecBoxLayout = QHBoxLayout(self.vecBox)

        self.sampleCheck = QCheckBox("Sample vector")
        self.sampleCheck.setChecked(True)

        self.stepCheck = QCheckBox("Window vector")
        self.stepCheck.setChecked(True)

        self.__vecBoxLayout.addWidget(self.sampleCheck)
        self.__vecBoxLayout.addWidget(self.stepCheck)

        # Format box widget
        self.fmtBox = QGroupBox("File format")
        self.__fmtBoxLayout = QGridLayout(self.fmtBox)

        self.__fmtLabel = QLabel("Format:")
        self.fmtCombo = QComboBox()
        fmt = ["CSV file (*.csv)"]

        try:
            import xlsxwriter
        except ModuleNotFoundError:
            pass
        if "xlsxwriter" in sys.modules:
            fmt.append("Excel file (*.xlsx)")

        self.fmtCombo.addItems(fmt)

        self.__fmtBoxLayout.addWidget(self.__fmtLabel, 0, 0)
        self.__fmtBoxLayout.addWidget(self.fmtCombo, 0, 1)

        # Setup button box
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.pathPicker, 0, 1)
        
        self.__layout.addWidget(self.paramBox, 1, 0, 1, 2)
        self.__layout.addWidget(self.vecBox, 2, 0, 1, 2)
        self.__layout.addWidget(self.fmtBox, 3, 0, 1, 2)

        self.__layout.addWidget(self.buttonBox, 4, 0, 1, 2)