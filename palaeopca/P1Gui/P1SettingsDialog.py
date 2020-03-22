# Standard library
from ast import literal_eval

# PyQt
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget, \
    QDialog, \
    QListWidget, \
    QListWidgetItem, \
    QLabel, \
    QScrollArea, \
    QPushButton, \
    QHBoxLayout, \
    QGridLayout, \
    QComboBox, \
    QLineEdit, \
    QSpinBox, \
    QCheckBox, \
    QMessageBox, \
    QGroupBox, \
    QVBoxLayout
    

# Maptlotlib
import matplotlib.pyplot as plt

# PalaeoPCA
import palaeopca
from palaeopca.P1Gui.P1PathPicker import P1PathPicker


def _icon(name, style = ""):
    icon = palaeopca.P1Utils.P1PixmapCache.getIcon(name, style)
    return icon

class P1SettingsDialog(QDialog):
    def __init__(self, parent = None):
        super(P1SettingsDialog, self).__init__(parent)

        self.__changes = False

        self.__setup_gui()

    def __setup_gui(self):
        self.__settings_list = QListWidget(self)
        self.__settings_list.setFixedWidth(200)

        self.__item_general = QListWidgetItem(_icon("tools", "solid"), "General", self.__settings_list) # Units, Volume
        self.__item_import = QListWidgetItem(_icon("download", "solid"), "Import", self.__settings_list)
        self.__item_zijder = QListWidgetItem(_icon("chart-line", "solid"), "Zijderveld plots", self.__settings_list)
        self.__item_sequence = QListWidgetItem(_icon("chart-bar", "solid"), "Sequence plots", self.__settings_list)
        self.__item_mesh = QListWidgetItem(_icon("chart-area", "solid"), "Mesh plots", self.__settings_list)

        self.__cat_label = QLabel("<span style='font-size:12pt; font-weight:600;'>General</span>")

        # Widgets
        self.__general_widget = P1GeneralSettings(self)
        self.__import_widget = P1ImportSettings(self)
        self.__zijder_widget = P1ZijderSettings(self)
        self.__sequence_widget = P1SequenceSettings(self)
        self.__mesh_widget = P1MeshSettings(self)

        # Scroll area
        self.__scroll_widget = QScrollArea()

        self.__scroll_widget.setWidget(self.__general_widget)
        self.__scroll_widget.takeWidget()
        self.__scroll_widget.setWidget(self.__import_widget)
        self.__scroll_widget.takeWidget()
        self.__scroll_widget.setWidget(self.__zijder_widget)
        self.__scroll_widget.takeWidget()
        self.__scroll_widget.setWidget(self.__sequence_widget)
        self.__scroll_widget.takeWidget()
        self.__scroll_widget.setWidget(self.__mesh_widget)
        self.__scroll_widget.takeWidget()

        # Buttons
        self.__ok_button = QPushButton("Ok")
        self.__chancel_button = QPushButton("Chancel")
        self.__apply_button = QPushButton("Apply")

        self.__button_layout = QHBoxLayout()
        self.__button_layout.addStretch()
        self.__button_layout.addWidget(self.__ok_button)
        self.__button_layout.addWidget(self.__chancel_button)
        self.__button_layout.addWidget(self.__apply_button)

        # Layout
        self.__layout = QGridLayout(self)
        self.__layout.addWidget(self.__settings_list, 0, 0, 2, 1)
        self.__layout.addWidget(self.__cat_label, 0, 1, 1, 1)
        self.__layout.addWidget(self.__scroll_widget, 1, 1, 1, 1)
        self.__layout.addLayout(self.__button_layout, 2, 0, 1, 2)

        self.__connect_gui()

        self.setWindowTitle("PalaeoPCA Settings")
        self.setMinimumSize(160, 160)
        self.resize(900, 480)

        self.__set_scroll_widget(0)

    def set_active(self, *args):
        self.__changes = True

    def __connect_gui(self):
        self.__settings_list.currentRowChanged.connect(self.__set_scroll_widget)
        self.__ok_button.clicked.connect(self.__on_ok_button_clicked)
        self.__chancel_button.clicked.connect(self.__on_chancel_button_clicked)
        self.__apply_button.clicked.connect(self.__on_apply_button_clicked)

    def __set_scroll_widget(self, currentRow):
        item = self.__settings_list.item(currentRow)
        self.__cat_label.setText("<span style='font-size:12pt; font-weight:600;'>{0}</span>".format(item.text()))
        self.__scroll_widget.takeWidget()

        if item.text() == "General":
            self.__scroll_widget.setWidget(self.__general_widget)
            self.__general_widget.load_settings()
        elif item.text() == "Import":
            self.__scroll_widget.setWidget(self.__import_widget)
            self.__import_widget.load_settings()
        elif item.text() == "Zijderveld plots":
            self.__scroll_widget.setWidget(self.__zijder_widget)
            self.__zijder_widget.load_settings()
        elif item.text() == "Sequence plots":
            self.__scroll_widget.setWidget(self.__sequence_widget)
            self.__sequence_widget.load_settings()
        elif item.text() == "Mesh plots":
            self.__scroll_widget.setWidget(self.__mesh_widget)
            self.__mesh_widget.load_settings()

    def __on_ok_button_clicked(self):
        if self.__changes:
            msgBox = QMessageBox(self)
            msgBox.setText("Some settings have been modified.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)

            action = msgBox.exec()

            if action == QMessageBox.Cancel:
                return
            elif action == QMessageBox.Discard:
                self.close()
            elif action == QMessageBox.Save:
                self.__saveAll()
                self.close()
        else:
            self.close()

    def __on_chancel_button_clicked(self):
        self.close()

    def __on_apply_button_clicked(self):
        self.__saveAll()

    def __saveAll(self):
        if self.__general_widget.loaded:
            self.__general_widget.save_settings()

        if self.__import_widget.loaded:
            self.__import_widget.save_settings()

        if self.__zijder_widget.loaded:
            self.__zijder_widget.save_settings()

        if self.__sequence_widget.loaded:
            self.__sequence_widget.save_settings()

        if self.__mesh_widget.loaded:
            self.__mesh_widget.save_settings()

        self.__changes = False

class P1GeneralSettings(QWidget):
    def __init__(self, parent = None):
        super(P1GeneralSettings, self).__init__(parent)
        
        self.__dlg = parent
        self.loaded = False

        self.__layout = QGridLayout(self)

        self.__label_unitsIn = QLabel("Input units")
        self.__label_unitsOut = QLabel("NRM output units")
        self.__label_volume = QLabel("Volume")

        self.__combo_unitsIn = QComboBox()
        self.__combo_unitsIn.addItems(["emu", "Am2", "A/m"])
        self.__combo_unitsOut = QComboBox()
        self.__combo_unitsOut.addItems(["emu", "Am2", "A/m"])
        self.__line_volume = QLineEdit()

        self.__layout.addWidget(self.__label_unitsIn, 0, 0)
        self.__layout.addWidget(self.__label_unitsOut, 1, 0)
        self.__layout.addWidget(self.__label_volume, 2, 0)

        self.__layout.addWidget(self.__combo_unitsIn, 0, 1)
        self.__layout.addWidget(self.__combo_unitsOut, 1, 1)
        self.__layout.addWidget(self.__line_volume, 2, 1)

    def load_settings(self):
        if not self.loaded:
            s = QSettings()

            self.__combo_unitsIn.setCurrentText(s.value("Units/Input", "emu"))
            self.__combo_unitsOut.setCurrentText(s.value("Units/Output", "A/m"))
            self.__line_volume.setText(str(s.value("Params/Volume", "10")))

            self.__combo_unitsIn.currentIndexChanged.connect(self.__dlg.set_active)
            self.__combo_unitsOut.currentIndexChanged.connect(self.__dlg.set_active)
            self.__line_volume.textEdited.connect(self.__dlg.set_active)

            self.loaded = True

    def save_settings(self):
        s = QSettings()

        s.setValue("Units/Input", self.__combo_unitsIn.currentText())
        s.setValue("Units/Output", self.__combo_unitsOut.currentText())
        s.setValue("Params/Volume", self.__line_volume.text())

class P1ImportSettings(QWidget):
    delimiters = {
        ",": ",",
        "{Space}": "\s+",
        "{Tab}": "\t",
        "|": "|",
        ":": ":",
        ";": ";",
    }
    def __init__(self, parent = None):
        super(P1ImportSettings, self).__init__(parent)
        
        self.__dlg = parent
        self.loaded = False
        self.__layout = QGridLayout(self)

        self.__label_num = QLabel("Numerics")
        self.__label_sep = QLabel("Delimiter")
        self.__label_header = QLabel("Skip top rows")
        self.__label_footer = QLabel("Skip bottom rows")

        self.__combo_num = QComboBox()
        self.__combo_num.addItems([".", ","])

        self.__combo_sep = QComboBox()
        self.__combo_sep.addItems([",", "\s+", "\t", "|", ":", ";"])

        self.__spin_header = QSpinBox()
        self.__spin_header.setMinimum(0)

        self.__spin_footer = QSpinBox()
        self.__spin_footer.setMinimum(0)

        self.__check_space = QCheckBox("Skip whitespaces")

        self.__layout.addWidget(self.__label_num, 0, 0)
        self.__layout.addWidget(self.__label_sep, 1, 0)
        self.__layout.addWidget(self.__label_header, 2, 0)
        self.__layout.addWidget(self.__label_footer, 3, 0)
        self.__layout.addWidget(self.__check_space, 4, 0, 1, 2)

        self.__layout.addWidget(self.__combo_num, 0, 1)
        self.__layout.addWidget(self.__combo_sep, 1, 1)
        self.__layout.addWidget(self.__spin_header, 2, 1)
        self.__layout.addWidget(self.__spin_footer, 3, 1)

    def load_settings(self):
        if not self.loaded:
            s = QSettings()

            self.__combo_num.setCurrentText(s.value("Import/Numerics", "."))
            self.__combo_sep.setCurrentText(s.value("Import/Separator", ","))
            self.__spin_header.setValue(int(s.value("Import/SkipHeader", 1)))
            self.__spin_footer.setValue(int(s.value("Import/SkipFooter", 1)))
            self.__check_space.setChecked(literal_eval(s.value("Import/SkipWhitespaces", "False")))

            self.__combo_num.currentIndexChanged.connect(self.__dlg.set_active)
            self.__combo_sep.currentIndexChanged.connect(self.__dlg.set_active)
            self.__spin_header.valueChanged.connect(self.__dlg.set_active)
            self.__spin_footer.valueChanged.connect(self.__dlg.set_active)
            self.__check_space.stateChanged.connect(self.__dlg.set_active)

            self.loaded = True

    def save_settings(self):
        s = QSettings()

        s.setValue("Import/Numerics", self.__combo_num.currentText())
        s.setValue("Import/Separator", self.__combo_sep.currentText())
        s.setValue("Import/SkipHeader", self.__spin_header.value())
        s.setValue("Import/SkipFooter", self.__spin_footer.value())
        if self.__check_space.isChecked():
            s.setValue("Import/SkipWhitespaces", "True")
        else:
            s.setValue("Import/SkipWhitespaces", "False")

class P1ZijderSettings(QWidget):
    def __init__(self, parent = None):
        super(P1ZijderSettings, self).__init__(parent)
        
        self.__dlg = parent
        self.loaded = False

        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Mpl style:")
        self.__pathPicker = P1PathPicker("file", "Matplotlib style files (*.mplstyle)", "Choose Matplotlib style file")

        # Figure box widgets
        self.figureBox = QGroupBox("Default Export Parameters")
        self.__figureLayout = QGridLayout(self.figureBox)

        self.__formatLabel = QLabel("File format")
        self.__format_combo = QComboBox()
        formats = [key for key in plt.gcf().canvas.get_supported_filetypes()]
        self.__format_combo.addItems(formats)
        
        self.__figureWLabel = QLabel("Figure width (in)")
        self.__figureHLabel = QLabel("Figure height (in)")
        self.__figureDPILabel = QLabel("Figure dpi")

        self.__figure_width = QLineEdit()
        self.__figure_height = QLineEdit()
        self.__figure_dpi = QLineEdit()

        self.__figureLayout.addWidget(self.__formatLabel, 0, 0)
        self.__figureLayout.addWidget(self.__format_combo, 0, 1)

        self.__figureLayout.addWidget(self.__figureWLabel, 0, 2)
        self.__figureLayout.addWidget(self.__figure_width, 0, 3)

        self.__figureLayout.addWidget(self.__figureDPILabel, 1, 0)
        self.__figureLayout.addWidget(self.__figure_dpi, 1, 1)

        self.__figureLayout.addWidget(self.__figureHLabel, 1, 2)
        self.__figureLayout.addWidget(self.__figure_height, 1, 3)

        # Directions box widgets
        self.dirBox = QGroupBox("Directions")
        self.__dirLayout = QGridLayout(self.dirBox)

        self.__xhLabel = QLabel("Horizontal x")
        self.__xvLabel = QLabel("Vertical x")
        self.__yLabel = QLabel("Horizontal y")
        self.__zLabel = QLabel("Vertical y")

        self.__xh_combo = QComboBox()
        self.__xh_combo.addItems(["N", "S", "E", "W"])

        self.__xv_combo = QComboBox()
        self.__xv_combo.addItems(["N", "S", "E", "W"])
        
        self.__y_combo = QComboBox()
        self.__y_combo.addItems(["N", "S", "E", "W"])

        self.__z_combo = QComboBox()
        self.__z_combo.addItems(["Up", "Down"])

        self.__dirLayout.addWidget(self.__xhLabel, 0, 0)
        self.__dirLayout.addWidget(self.__xh_combo, 0, 1)
        self.__dirLayout.addWidget(self.__yLabel, 0, 2)
        self.__dirLayout.addWidget(self.__y_combo, 0, 3)

        self.__dirLayout.addWidget(self.__xvLabel, 1, 0)
        self.__dirLayout.addWidget(self.__xv_combo, 1, 1)
        self.__dirLayout.addWidget(self.__zLabel, 1, 2)
        self.__dirLayout.addWidget(self.__z_combo, 1, 3)

        # PCA box widgets
        self.PCABox = QGroupBox("PCA Results")
        self.__pcaLayout = QVBoxLayout(self.PCABox)

        self.__mark_check = QCheckBox("Mark steps used in PCA")
        self.__anno_check = QCheckBox("Add PCA results to legend")
        self.__line_check = QCheckBox("Plot PCA lines")

        self.__pcaLayout.addWidget(self.__mark_check)
        self.__pcaLayout.addWidget(self.__anno_check)
        self.__pcaLayout.addWidget(self.__line_check)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.__pathPicker, 0, 1)
        
        self.__layout.addWidget(self.dirBox, 1, 0, 1, 2)
        self.__layout.addWidget(self.PCABox, 2, 0, 1, 2)
        self.__layout.addWidget(self.figureBox, 3, 0, 1, 2)

    def load_settings(self):
        if not self.loaded:
            s = QSettings()

            self.__pathPicker.setPath(s.value("Zijder/Style", "./palaeopca/P1Mpl/styles/zijder.mplstyle"))

            self.__format_combo.setCurrentText(s.value("Zijder/fmt", "png"))
            size = literal_eval(s.value("Zijder/Size", "(5, 5)"))
            self.__figure_width.setText(str(size[0]))
            self.__figure_height.setText(str(size[1]))
            self.__figure_dpi.setText(str(s.value("Zijder/dpi", "300")))

            self.__xh_combo.setCurrentText(s.value("Zijder/xh", "N"))
            self.__xv_combo.setCurrentText(s.value("Zijder/xv", "N"))
            self.__y_combo.setCurrentText(s.value("Zijder/y", "W"))
            self.__z_combo.setCurrentText(s.value("Zijder/z", "Up"))

            self.__mark_check.setChecked(literal_eval(s.value("Zijder/mark", "False")))
            self.__anno_check.setChecked(literal_eval(s.value("Zijder/anno", "False")))
            self.__line_check.setChecked(literal_eval(s.value("Zijder/line", "False")))

            self.__pathPicker.lineChanged.connect(self.__dlg.set_active)
            self.__figure_width.textEdited.connect(self.__dlg.set_active)
            self.__figure_height.textEdited.connect(self.__dlg.set_active)
            self.__figure_dpi.textEdited.connect(self.__dlg.set_active)
            self.__format_combo.currentIndexChanged.connect(self.__dlg.set_active)

            self.__xh_combo.currentIndexChanged.connect(self.__dlg.set_active)
            self.__xv_combo.currentIndexChanged.connect(self.__dlg.set_active)
            self.__y_combo.currentIndexChanged.connect(self.__dlg.set_active)
            self.__z_combo.currentIndexChanged.connect(self.__dlg.set_active)

            self.__mark_check.stateChanged.connect(self.__dlg.set_active)
            self.__anno_check.stateChanged.connect(self.__dlg.set_active)
            self.__line_check.stateChanged.connect(self.__dlg.set_active)

            self.loaded = True

    def save_settings(self):
        s = QSettings()

        s.setValue("Zijder/Style", self.__pathPicker.getPath())

        s.setValue("Zijder/fmt", self.__format_combo.currentText())
        s.setValue("Zijder/Size", "({0}, {1})".format(self.__figure_width.text(), self.__figure_height.text()))
        s.setValue("Zijder/dpi", self.__figure_dpi.text())

        s.setValue("Zijder/xh", self.__xh_combo.currentText())
        s.setValue("Zijder/xv", self.__xv_combo.currentText())
        s.setValue("Zijder/y", self.__y_combo.currentText())
        s.setValue("Zijder/z", self.__z_combo.currentText())

        if self.__mark_check.isChecked():
            s.setValue("Zijder/mark", "True")
        else:
            s.setValue("Zijder/mark", "False")

        if self.__anno_check.isChecked():
            s.setValue("Zijder/anno", "True")
        else:
            s.setValue("Zijder/anno", "False")

        if self.__line_check.isChecked():
            s.setValue("Zijder/line", "True")
        else:
            s.setValue("Zijder/line", "False")

class P1SequenceSettings(QWidget):
    def __init__(self, parent = None):
        super(P1SequenceSettings, self).__init__(parent)
        
        self.__dlg = parent
        self.loaded = False

        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Mpl style:")
        self.__pathPicker = P1PathPicker("file", "Matplotlib style files (*.mplstyle)", "Choose Matplotlib style file")

        # Figure box widgets
        self.figureBox = QGroupBox("Default Export Parameters")
        self.__figureLayout = QGridLayout(self.figureBox)

        self.__formatLabel = QLabel("File format")
        self.__format_combo = QComboBox()
        formats = [key for key in plt.gcf().canvas.get_supported_filetypes()]
        self.__format_combo.addItems(formats)
        
        self.__figureWLabel = QLabel("Figure width (in)")
        self.__figureHLabel = QLabel("Figure height (in)")
        self.__figureDPILabel = QLabel("Figure dpi")

        self.__figure_width = QLineEdit()
        self.__figure_height = QLineEdit()
        self.__figure_dpi = QLineEdit()

        self.__figureLayout.addWidget(self.__formatLabel, 0, 0)
        self.__figureLayout.addWidget(self.__format_combo, 0, 1)

        self.__figureLayout.addWidget(self.__figureWLabel, 0, 2)
        self.__figureLayout.addWidget(self.__figure_width, 0, 3)

        self.__figureLayout.addWidget(self.__figureDPILabel, 1, 0)
        self.__figureLayout.addWidget(self.__figure_dpi, 1, 1)

        self.__figureLayout.addWidget(self.__figureHLabel, 1, 2)
        self.__figureLayout.addWidget(self.__figure_height, 1, 3)

        # Parameter box widgets
        self.paramBox = QGroupBox("Parameters")
        self.__paramLayout = QGridLayout(self.paramBox)

        self.__nrm_check = QCheckBox("NRM")
        self.__inc_check = QCheckBox("Inclination")
        self.__dec_check = QCheckBox("Declination")
        self.__madp_check = QCheckBox("MADp")
        self.__mado_check = QCheckBox("MADo")
        self.__inv_check = QCheckBox("Invert Y")

        self.__paramLayout.addWidget(self.__nrm_check, 0, 0)
        self.__paramLayout.addWidget(self.__inc_check, 0, 1)
        self.__paramLayout.addWidget(self.__dec_check, 1, 0)
        self.__paramLayout.addWidget(self.__madp_check, 1, 1)
        self.__paramLayout.addWidget(self.__mado_check, 2, 0)
        self.__paramLayout.addWidget(self.__inv_check, 2, 1)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.__pathPicker, 0, 1)
        
        self.__layout.addWidget(self.figureBox, 1, 0, 1, 2)
        self.__layout.addWidget(self.paramBox, 2, 0, 1, 2)

    def load_settings(self):
        if not self.loaded:
            s = QSettings()

            self.__pathPicker.setPath(s.value("Sequence/Style", "./palaeopca/P1Mpl/styles/sequence.mplstyle"))

            self.__format_combo.setCurrentText(s.value("Sequence/fmt", "png"))
            size = literal_eval(s.value("Sequence/Size", "(5, 5)"))
            self.__figure_width.setText(str(size[0]))
            self.__figure_height.setText(str(size[1]))
            self.__figure_dpi.setText(str(s.value("Sequence/dpi", "300")))

            self.__nrm_check.setChecked(literal_eval(s.value("Sequence/NRM", "True")))
            self.__inc_check.setChecked(literal_eval(s.value("Sequence/Incl", "True")))
            self.__dec_check.setChecked(literal_eval(s.value("Sequence/Decl", "True")))
            self.__madp_check.setChecked(literal_eval(s.value("Sequence/MADp", "True")))
            self.__mado_check.setChecked(literal_eval(s.value("Sequence/MADo", "True")))
            self.__inv_check.setChecked(literal_eval(s.value("Sequence/invertY", "True")))

            self.__pathPicker.lineChanged.connect(self.__dlg.set_active)
            self.__figure_width.textEdited.connect(self.__dlg.set_active)
            self.__figure_height.textEdited.connect(self.__dlg.set_active)
            self.__figure_dpi.textEdited.connect(self.__dlg.set_active)
            self.__format_combo.currentIndexChanged.connect(self.__dlg.set_active)

            self.__nrm_check.stateChanged.connect(self.__dlg.set_active)
            self.__inc_check.stateChanged.connect(self.__dlg.set_active)
            self.__dec_check.stateChanged.connect(self.__dlg.set_active)
            self.__madp_check.stateChanged.connect(self.__dlg.set_active)
            self.__mado_check.stateChanged.connect(self.__dlg.set_active)
            self.__inv_check.stateChanged.connect(self.__dlg.set_active)

            self.loaded = True

    def save_settings(self):
        s = QSettings()

        s.setValue("Sequence/Style", self.__pathPicker.getPath())

        s.setValue("Sequence/fmt", self.__format_combo.currentText())
        s.setValue("Sequence/Size", "({0}, {1})".format(self.__figure_width.text(), self.__figure_height.text()))
        s.setValue("Sequence/dpi", self.__figure_dpi.text())
        if self.__nrm_check.isChecked():
            s.setValue("Sequence/NRM", "True")
        else:
            s.setValue("Sequence/NRM", "False")

        if self.__inc_check.isChecked():
            s.setValue("Sequence/Incl", "True")
        else:
            s.setValue("Sequence/Incl", "False")

        if self.__dec_check.isChecked():
            s.setValue("Sequence/Decl", "True")
        else:
            s.setValue("Sequence/Decl", "False")

        if self.__madp_check.isChecked():
            s.setValue("Sequence/MADp", "True")
        else:
            s.setValue("Sequence/MADp", "False")

        if self.__mado_check.isChecked():
            s.setValue("Sequence/MADo", "True")
        else:
            s.setValue("Sequence/MADo", "False")

        if self.__inv_check.isChecked():
            s.setValue("Sequence/invertY", "True")
        else:
            s.setValue("Sequence/invertY", "False")

class P1MeshSettings(QWidget):
    def __init__(self, parent = None):
        super(P1MeshSettings, self).__init__(parent)
        
        self.__dlg = parent
        self.loaded = False

        self.__layout = QGridLayout(self)
        self.__layout.setSpacing(2)
        self.__layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.__layout)

        self.__fileLabel = QLabel("Mpl style:")
        self.__pathPicker = P1PathPicker("file", "Matplotlib style files (*.mplstyle)", "Choose Matplotlib style file")

        # Figure box widget
        self.figureBox = QGroupBox("Default Export Parameters")
        self.__figureLayout = QGridLayout(self.figureBox)

        self.__formatLabel = QLabel("File format")
        self.__format_combo = QComboBox()
        formats = [key for key in plt.gcf().canvas.get_supported_filetypes()]
        self.__format_combo.addItems(formats)
        
        self.__figureWLabel = QLabel("Figure width (in)")
        self.__figureHLabel = QLabel("Figure height (in)")
        self.__figureDPILabel = QLabel("Figure dpi")

        self.__figure_width = QLineEdit()
        self.__figure_height = QLineEdit()
        self.__figure_dpi = QLineEdit()

        self.__figureLayout.addWidget(self.__formatLabel, 0, 0)
        self.__figureLayout.addWidget(self.__format_combo, 0, 1)

        self.__figureLayout.addWidget(self.__figureWLabel, 0, 2)
        self.__figureLayout.addWidget(self.__figure_width, 0, 3)

        self.__figureLayout.addWidget(self.__figureDPILabel, 1, 0)
        self.__figureLayout.addWidget(self.__figure_dpi, 1, 1)

        self.__figureLayout.addWidget(self.__figureHLabel, 1, 2)
        self.__figureLayout.addWidget(self.__figure_height, 1, 3)

        # Parameter box widget
        self.paramBox = QGroupBox("Parameters")
        self.__paramLayout = QGridLayout(self.paramBox)

        self.__nrm_check = QCheckBox("NRM")
        self.__inc_check = QCheckBox("Inclination")
        self.__dec_check = QCheckBox("Declination")
        self.__madp_check = QCheckBox("MADp")
        self.__mado_check = QCheckBox("MADo")
        self.__inv_check = QCheckBox("Invert Y")

        self.__paramLayout.addWidget(self.__nrm_check, 0, 0)
        self.__paramLayout.addWidget(self.__inc_check, 0, 1)
        self.__paramLayout.addWidget(self.__dec_check, 1, 0)
        self.__paramLayout.addWidget(self.__madp_check, 1, 1)
        self.__paramLayout.addWidget(self.__mado_check, 2, 0)
        self.__paramLayout.addWidget(self.__inv_check, 2, 1)

        # Colormaps box widget
        self.cmapBox = QGroupBox("Colormaps")
        self.__cmapLayout = QGridLayout(self.cmapBox)

        self.__cmapNRMLabel = QLabel("NRM")
        self.__cmapIncLabel = QLabel("Inclination")
        self.__cmapDecLabel = QLabel("Declination")
        self.__cmapMADpLabel = QLabel("MADp")
        self.__cmapMADoLabel = QLabel("MADo")

        self.__cmapNRMCombo = QComboBox()
        self.__cmapIncCombo = QComboBox()
        self.__cmapDecCombo = QComboBox()
        self.__cmapMADpCombo = QComboBox()
        self.__cmapMADoCombo = QComboBox()

        cmaps = plt.colormaps()

        self.__cmapNRMCombo.addItems(cmaps)
        self.__cmapIncCombo.addItems(cmaps)
        self.__cmapDecCombo.addItems(cmaps)
        self.__cmapMADpCombo.addItems(cmaps)
        self.__cmapMADoCombo.addItems(cmaps)

        self.__cmapLayout.addWidget(self.__cmapNRMLabel, 0, 0)
        self.__cmapLayout.addWidget(self.__cmapIncLabel, 1, 0)
        self.__cmapLayout.addWidget(self.__cmapDecLabel, 2, 0)
        self.__cmapLayout.addWidget(self.__cmapMADpLabel, 3, 0)
        self.__cmapLayout.addWidget(self.__cmapMADoLabel, 4, 0)

        self.__cmapLayout.addWidget(self.__cmapNRMCombo, 0, 1)
        self.__cmapLayout.addWidget(self.__cmapIncCombo, 1, 1)
        self.__cmapLayout.addWidget(self.__cmapDecCombo, 2, 1)
        self.__cmapLayout.addWidget(self.__cmapMADpCombo, 3, 1)
        self.__cmapLayout.addWidget(self.__cmapMADoCombo, 4, 1)

        self.__layout.addWidget(self.__fileLabel, 0, 0)
        self.__layout.addWidget(self.__pathPicker, 0, 1)
        
        self.__layout.addWidget(self.paramBox, 1, 0, 1, 2)
        self.__layout.addWidget(self.cmapBox, 2, 0, 1, 2)
        self.__layout.addWidget(self.figureBox, 3, 0, 1, 2)

    def load_settings(self):
        if not self.loaded:
            s = QSettings()

            self.__pathPicker.setPath(s.value("Mesh/Style", "./palaeopca/P1Mpl/styles/sequence.mplstyle"))

            self.__format_combo.setCurrentText(s.value("Mesh/fmt", "png"))
            size = literal_eval(s.value("Mesh/Size", "(5, 5)"))
            self.__figure_width.setText(str(size[0]))
            self.__figure_height.setText(str(size[1]))
            self.__figure_dpi.setText(str(s.value("Mesh/dpi", "300")))

            self.__nrm_check.setChecked(literal_eval(s.value("Mesh/NRM", "True")))
            self.__inc_check.setChecked(literal_eval(s.value("Mesh/Incl", "True")))
            self.__dec_check.setChecked(literal_eval(s.value("Mesh/Decl", "True")))
            self.__madp_check.setChecked(literal_eval(s.value("Mesh/MADp", "True")))
            self.__mado_check.setChecked(literal_eval(s.value("Mesh/MADo", "True")))
            self.__inv_check.setChecked(literal_eval(s.value("Mesh/invertY", "True")))

            self.__cmapNRMCombo.setCurrentText(s.value("Mesh/NRMcmap", "tab20c"))
            self.__cmapIncCombo.setCurrentText(s.value("Mesh/INCcmap", "PRGn"))
            self.__cmapDecCombo.setCurrentText(s.value("Mesh/DECcmap", "PRGn"))
            self.__cmapMADpCombo.setCurrentText(s.value("Mesh/MADpcmap", "hot"))
            self.__cmapMADoCombo.setCurrentText(s.value("Mesh/MADocmap", "hot"))

            self.__pathPicker.lineChanged.connect(self.__dlg.set_active)
            self.__figure_width.textEdited.connect(self.__dlg.set_active)
            self.__figure_height.textEdited.connect(self.__dlg.set_active)
            self.__figure_dpi.textEdited.connect(self.__dlg.set_active)
            self.__format_combo.currentIndexChanged.connect(self.__dlg.set_active)

            self.__nrm_check.stateChanged.connect(self.__dlg.set_active)
            self.__inc_check.stateChanged.connect(self.__dlg.set_active)
            self.__dec_check.stateChanged.connect(self.__dlg.set_active)
            self.__madp_check.stateChanged.connect(self.__dlg.set_active)
            self.__mado_check.stateChanged.connect(self.__dlg.set_active)
            self.__inv_check.stateChanged.connect(self.__dlg.set_active)

            self.__cmapNRMCombo.currentIndexChanged.connect(self.__dlg.set_active)
            self.__cmapIncCombo.currentIndexChanged.connect(self.__dlg.set_active)
            self.__cmapDecCombo.currentIndexChanged.connect(self.__dlg.set_active)
            self.__cmapMADpCombo.currentIndexChanged.connect(self.__dlg.set_active)
            self.__cmapMADoCombo.currentIndexChanged.connect(self.__dlg.set_active)

            self.loaded = True

    def save_settings(self):
        s = QSettings()

        s.setValue("Mesh/Style", self.__pathPicker.getPath())

        s.setValue("Mesh/fmt", self.__format_combo.currentText())
        s.setValue("Mesh/Size", "({0}, {1})".format(self.__figure_width.text(), self.__figure_height.text()))
        s.setValue("Mesh/dpi", self.__figure_dpi.text())

        if self.__nrm_check.isChecked():
            s.setValue("Mesh/NRM", "True")
        else:
            s.setValue("Mesh/NRM", "False")

        if self.__inc_check.isChecked():
            s.setValue("Mesh/Incl", "True")
        else:
            s.setValue("Mesh/Incl", "False")

        if self.__dec_check.isChecked():
            s.setValue("Mesh/Decl", "True")
        else:
            s.setValue("Mesh/Decl", "False")

        if self.__madp_check.isChecked():
            s.setValue("Mesh/MADp", "True")
        else:
            s.setValue("Mesh/MADp", "False")

        if self.__mado_check.isChecked():
            s.setValue("Mesh/MADo", "True")
        else:
            s.setValue("Mesh/MADo", "False")

        if self.__inv_check.isChecked():
            s.setValue("Mesh/invertY", "True")
        else:
            s.setValue("Mesh/invertY", "False")

        s.setValue("Mesh/NRMcmap", self.__cmapNRMCombo.currentText())
        s.setValue("Mesh/INCcmap", self.__cmapIncCombo.currentText())
        s.setValue("Mesh/DECcmap", self.__cmapDecCombo.currentText())
        s.setValue("Mesh/MADpcmap", self.__cmapMADpCombo.currentText())
        s.setValue("Mesh/MADocmap", self.__cmapMADoCombo.currentText())