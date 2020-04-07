## Standard library
import os
import shutil
import re
import configparser
from ast import literal_eval
import webbrowser

## Qt
from PyQt5.QtCore import \
    Qt, \
    pyqtSlot, \
    QModelIndex, \
    QPoint, \
    QCoreApplication, \
    QSettings, \
    pyqtSlot

from PyQt5.QtWidgets import QMainWindow, \
    QAction, \
    QMenu, \
    QSplitter, \
    QDialog, \
    QScrollArea, \
    QTreeWidgetItem, \
    QSizePolicy, \
    QMessageBox, \
    QToolBar, \
    QStatusBar, \
    QMdiArea, \
    QMdiSubWindow, \
    QFileDialog, \
    QMessageBox

from PyQt5.QtGui import QIcon

# PalaeoPCA
import palaeopca
from palaeopca.P1Gui.P1DataWindow import P1DataWindow
from palaeopca.P1Backend.P1DataObject import P1DataObject
from palaeopca.P1Gui.P1AboutDialog import P1AboutDialog

def _icon(name, style = ""):
    icon = palaeopca.P1Utils.P1PixmapCache.getIcon(name, style)
    return icon

class P1MainWindow(QMainWindow):
    def __init__(self, parent = None):
        # Init QMainWindow
        super().__init__(parent)

        # Set attributes and window title
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(_icon("project-diagram", "solid"))
        self.setWindowTitle("PalaeoPCA {0}".format(palaeopca.__version__))

        # Add statusbar
        self.__statusbar = QStatusBar(self)
        self.setStatusBar(self.__statusbar)

        # Setup layout
        self.__setup_layout()

    def __setup_layout(self):
        """
        """
        self.__setup_actions()
        self.__setup_menus()

        cw = QMdiArea(self)
        self.setCentralWidget(cw)

        self.__connect_gui()

    def __setup_actions(self):
        # File actions
        self.actionSettings = QAction(self)
        self.actionSettings.setIcon(_icon("cogs", "solid"))
        self.actionSettings.setText("Settings")

        self.actionExit = QAction(self)
        self.actionExit.setIcon(_icon("sign-out-alt", "solid"))
        self.actionExit.setText("Exit")
        
        # Import actions
        self.action_import = QAction(self)
        self.action_import.setIcon(_icon("file-import", "solid"))
        self.action_import.setText("Import")

        self.action_quick_import = QAction(self)
        self.action_quick_import.setIcon(_icon("file-upload", "solid"))
        self.action_quick_import.setText("Quick Import")

        # Export actions
        #self.action_export_zijder = QAction(self)
        #self.action_export_zijder.setIcon(_icon("SP_DialogSaveButton"))
        #self.action_export_zijder.setText("Export zijderveld plots")

        #self.action_export_seq = QAction(self)
        #self.action_export_seq.setIcon(_icon("SP_DialogSaveButton"))
        #self.action_export_seq.setText("Export sequence plot")

        # Help actions
        self.action_docs = QAction(self)
        self.action_docs.setIcon(_icon("book", "solid"))
        self.action_docs.setText("Documentation")

        self.action_about = QAction(self)
        #self.action_about.setIcon(_icon())
        self.action_about.setText("About")

    def __setup_menus(self):
        menubar = self.menuBar()

        # File menu
        menuFile = QMenu("File", menubar)
        menuFile.addAction(self.actionSettings)
        menuFile.addSeparator()
        menuFile.addAction(self.actionExit)

        # Import menu
        menuImport = QMenu("Import", menubar)
        menuImport.addAction(self.action_import)
        menuImport.addAction(self.action_quick_import)

        # Export menu
        #menuExport = QMenu("Export", menubar)
        #menuExport.addAction(self.action_export_zijder)
        #menuExport.addAction(self.action_export_seq)

        # Help menu
        menuHelp = QMenu("Help", menubar)
        menuHelp.addAction(self.action_docs)
        menuHelp.addAction(self.action_about)

        # Setup
        menubar.addMenu(menuFile)
        menubar.addMenu(menuImport)
        #menubar.addMenu(menuExport)
        menubar.addMenu(menuHelp)

        #

    def __connect_gui(self):
        self.actionSettings.triggered.connect(self.on_settings_triggered)
        self.actionExit.triggered.connect(self.close)

        self.action_import.triggered.connect(self.on_import_triggered)
        self.action_quick_import.triggered.connect(self.on_quick_import_triggered)

        self.action_docs.triggered.connect(self.on_docs_triggered)
        self.action_about.triggered.connect(self.on_about_triggered)
    
    @pyqtSlot()
    def on_settings_triggered(self):
        from palaeopca.P1Gui.P1SettingsDialog import P1SettingsDialog

        dlg = P1SettingsDialog(self)
        dlg.setWindowIcon(_icon("cogs", "solid"))
        dlg.show()

    @pyqtSlot()
    def on_import_triggered(self):
        from palaeopca.P1Gui.P1ImportDialog import P1ImportDialog
        dlg = P1ImportDialog(self)
        dlg.setWindowIcon(_icon("file-import", "solid"))

        if dlg.exec_() == QDialog.Accepted:
            try:
                self.open_data_window(dlg.pathPicker.getPath(), dlg.data)
            except AttributeError:
                QMessageBox.warning(self, "Import warning", "Error while reading input file!", QMessageBox.Ok)

    @pyqtSlot()
    def on_quick_import_triggered(self):
        dialog = QFileDialog()
        infile = dialog.getOpenFileName(None, "Choose data file to open", "", "All Files (*);;CSV files (*.csv);;Text files (*.txt)")[0]

        if infile == "":
            return

        s = QSettings()
        skip_header = int(s.value("Import/SkipHeader", 1))
        skip_footer = int(s.value("Import/SkipFooter", 0))
        numerics = s.value("Import/Numeric", ".")
        sep = s.value("Import/Separator", ",")
        skip = literal_eval(s.value("Import/SkipWhitespaces", "False"))

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
        except ValueError:
            QMessageBox.warning(self, "Import warning", "Error while reading input file!", QMessageBox.Ok)
            return

        data.set_units(s.value("Units/Input", "emu"))

        self.open_data_window(infile, data)

    @pyqtSlot()
    def on_docs_triggered(self):
        url = palaeopca.basedir.replace("\\", "/") + "/../docs/index.html"

        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("Open documentation")
        msgBox.setText("Documentation will open in external browser window.")
        msgBox.setInformativeText("URL: {0}".format(url))
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Ok)
        
        if msgBox.exec() == QMessageBox.Ok:
            webbrowser.get('windows-default').open(url, new=2)

    @pyqtSlot()
    def on_about_triggered(self):
        dialog = P1AboutDialog(self)
        dialog.show()

    def open_data_window(self, infile, data):
        subwindow = QMdiSubWindow(self.centralWidget())
        subwindow.setWindowTitle("Data - {0}".format(infile))
        subwindow.setWidget(P1DataWindow(subwindow))
        subwindow.setAttribute(Qt.WA_DeleteOnClose)
        subwindow.widget().set_data(data)
        subwindow.show()