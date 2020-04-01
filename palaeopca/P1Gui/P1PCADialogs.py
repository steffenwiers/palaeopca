from typing import List
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QComboBox, QLineEdit, QDialogButtonBox, QSpinBox, QCheckBox


class P1SingleIntervalDialog(QDialog):
    def __init__(self, steps: List, parent = None):
        super(P1SingleIntervalDialog, self).__init__(parent)
        self.setWindowTitle("Run Single Interval PCA")

        s = QSettings()

        self.__layout = QFormLayout(self)
        
        self.minCombo = QComboBox(self)
        self.minCombo.addItems(steps)
        self.__layout.addRow(QLabel("Minimum step:"), self.minCombo)
        
        self.maxCombo = QComboBox(self)
        self.maxCombo.addItems(steps)
        self.maxCombo.setCurrentIndex(len(steps) - 1)
        self.__layout.addRow(QLabel("Maximum step:"), self.maxCombo)

        self.NRMUnitCombo = QComboBox(self)
        self.NRMUnitCombo.addItems(["emu", "Am2", "A/m"])
        self.NRMUnitCombo.setCurrentText(s.value("Units/Output", "A/m"))
        self.__layout.addRow(QLabel("NRM unit:"), self.NRMUnitCombo)

        self.volumeLine = QLineEdit(self)
        self.volumeLine.setText(s.value("Params/Volume", 10))
        self.__layout.addRow(QLabel("Volume (g/cc)"), self.volumeLine)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addRow(self.buttonBox)

class P1BestFitDialog(QDialog):
    def __init__(self, steps: List, parent = None):
        super(P1BestFitDialog, self).__init__(parent)
        self.setWindowTitle("Run Best Fit PCA")

        s = QSettings()

        self.__layout = QFormLayout(self)
        
        self.minSpin = QSpinBox(self)
        self.minSpin.setMinimum(3)
        self.minSpin.setMaximum(len(steps))
        self.__layout.addRow(QLabel("Minimum steps:"), self.minSpin)
        
        self.NRMUnitCombo = QComboBox(self)
        self.NRMUnitCombo.addItems(["emu", "Am2", "A/m"])
        self.NRMUnitCombo.setCurrentText(s.value("Units/Output", "A/m"))
        self.__layout.addRow(QLabel("NRM unit:"), self.NRMUnitCombo)

        self.volumeLine = QLineEdit(self)
        self.volumeLine.setText(str(s.value("Params/Volume", "10")))
        self.__layout.addRow(QLabel("Volume (g/cc)"), self.volumeLine)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addRow(self.buttonBox)

class P1MeshDialog(QDialog):
    def __init__(self, steps: List, parent = None):
        super(P1MeshDialog, self).__init__(parent)
        self.setWindowTitle("Run Mesh PCA")

        self.__layout = QFormLayout(self)
        
        self.stepSpin = QSpinBox(self)
        self.stepSpin.setMinimum(3)
        self.stepSpin.setMaximum(len(steps))

        self.checkDifference = QCheckBox(self)

        self.__layout.addRow(QLabel("Steps:"), self.stepSpin)
        self.__layout.addRow(QLabel("Difference Vector"), self.checkDifference)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.__layout.addRow(self.buttonBox)