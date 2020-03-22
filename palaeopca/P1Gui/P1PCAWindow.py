# Standard library
import sys
from ast import literal_eval

# Qt
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot, QSettings
from PyQt5.QtWidgets import QWidget, QGridLayout, QTableView, QMenuBar, QMenu, QToolButton, QComboBox, QAction, QTabWidget, QVBoxLayout, QFileDialog, QMessageBox, QDialog

# Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# Numpy
import numpy as np

# palaeopca
from palaeopca.P1Backend.P1DataObject import P1DataObject
from palaeopca.P1Backend.P1Backend import P1Backend

from palaeopca.P1Gui.P1ResultsModel import P1ResultsModel
from palaeopca.P1Gui.P1ProgressBar import P1ProgressBar

from palaeopca.P1Mpl.P1Zijder import zijder_plot
from palaeopca.P1Mpl.P1Sequence import sequence_plot

import palaeopca.P1Utils.P1PixmapCache


class P1PCAWindow(QWidget):
    def __init__(self, parent = None):
        super(P1PCAWindow, self).__init__(parent)

        s = QSettings()
        self.__anno = literal_eval(s.value("Zijder/anno", "True"))
        self.__mark = literal_eval(s.value("Zijder/mark", "True"))
        self.__line = literal_eval(s.value("Zijder/line", "True"))

        self.__setupGui()
        self.__connectGui()

    def __setupGui(self):
        self.__layout = QGridLayout(self)
        self.__setupMenu()

        self.__table = QTableView()
        self.__model = None

        self.__setupZijderTab()
        
        self.__sequence_figure_widget = QWidget()
        self.__sequence_figure_widget.setLayout(QVBoxLayout())
        self.__sequence_figure = Figure(figsize = (3, 3), dpi = 150)
        self.__sequence_canvas = FigureCanvasQTAgg(self.__sequence_figure)
        self.__sequence_toolbar = NavigationToolbar2QT(self.__sequence_canvas, self.__sequence_figure_widget)
        self.__sequence_figure_widget.layout().addWidget(self.__sequence_toolbar)
        self.__sequence_figure_widget.layout().addWidget(self.__sequence_canvas)

        self.__tabs = QTabWidget()
        self.__tabs.addTab(self.__table, "PCA Results")
        self.__tabs.addTab(self.__zijder_widget, "Zijderveld Plots")
        self.__tabs.addTab(self.__sequence_figure_widget, "Sequence Plot")

        self.__layout.addWidget(self.__tabs)

    def __setupMenu(self):
        self.__menu = QMenuBar()

        self.__fileMenu = QMenu("File")

        self.__action_close = QAction(self)
        self.__action_close.setIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("sign-out-alt", "solid"))
        self.__action_close.setText("Close")

        self.__fileMenu.addAction(self.__action_close)

        self.__exportMenu = QMenu("Export")

        self.__action_export_data = QAction(self)
        self.__action_export_data.setIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("file-export", "solid"))
        self.__action_export_data.setText("Export data")

        self.__action_export_zijder = QAction(self)
        self.__action_export_zijder.setIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("chart-line", "solid"))
        self.__action_export_zijder.setText("Export Zijderveld plots")

        self.__action_export_sequence = QAction(self)
        self.__action_export_sequence.setIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("chart-bar", "solid"))
        self.__action_export_sequence.setText("Export sequence plot")

        self.__exportMenu.addAction(self.__action_export_data)
        self.__exportMenu.addAction(self.__action_export_zijder)
        self.__exportMenu.addAction(self.__action_export_sequence)

        self.__menu.addMenu(self.__fileMenu)
        self.__menu.addMenu(self.__exportMenu)

        self.__layout.setMenuBar(self.__menu)

    def __setupZijderTab(self):
        self.__zijder_widget = QWidget()
        self.__zijder_layout = QGridLayout()

        self.__zijder_figure = Figure(figsize = (4, 4), dpi = 150)
        self.__zijder_canvas = FigureCanvasQTAgg(self.__zijder_figure)

        self.__zijder_toolbar = NavigationToolbar2QT(self.__zijder_canvas, self.__zijder_widget)

        self.__prevButton = QToolButton(self)
        self.__prevButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.__prevButton.setIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("chevron-left", "solid"))

        self.__sampleCombo = QComboBox(self)

        self.__nextButton = QToolButton(self)
        self.__nextButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.__nextButton.setIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("chevron-right", "solid"))

        self.__zijder_layout.addWidget(self.__zijder_toolbar, 0, 0, 1, 1)
        self.__zijder_layout.addWidget(self.__prevButton, 0, 1, 1, 1)
        self.__zijder_layout.addWidget(self.__sampleCombo, 0, 2, 1, 1)
        self.__zijder_layout.addWidget(self.__nextButton, 0, 3, 1, 1)
        self.__zijder_layout.addWidget(self.__zijder_canvas, 1, 0, 1, 4)
        self.__zijder_layout.setRowStretch(1, 10)

        self.__zijder_widget.setLayout(self.__zijder_layout)

    def __connectGui(self):
        self.__action_close.triggered.connect(self.parent().close)

        self.__action_export_data.triggered.connect(self.__export_data)
        self.__action_export_zijder.triggered.connect(self.__export_zijder)
        self.__action_export_sequence.triggered.connect(self.__export_sequence)

        self.__sampleCombo.currentIndexChanged.connect(self.__update_zijder)
        self.__prevButton.clicked.connect(self.__on_prev_button_clicked)
        self.__nextButton.clicked.connect(self.__on_next_button_clicked)
    
    def set_data(self, data: P1DataObject, results: np.ndarray, NRM_unit: str = "A/m"):
        self.__data = data
        self.__results = results
        self.__nrm_unit = NRM_unit

        self.__model = P1ResultsModel(results, ["SampleID/Depth", "NRM ({0})".format(NRM_unit), "Inclination (°)", "Declination (°)", "MADp (°)", "MADo (°)", "Min step", "Max step"])
        self.__table.setModel(self.__model)

        self.__sampleCombo.currentIndexChanged.disconnect(self.__update_zijder)
        self.__sampleCombo.clear()
        self.__sampleCombo.addItems([str(x) for x in self.__data.get_samples().tolist()])
        self.__sampleCombo.currentIndexChanged.connect(self.__update_zijder)

        self.__update_zijder(0)
        self.__update_sequence()

    @pyqtSlot()
    def __on_prev_button_clicked(self):
        self.__sampleCombo.setCurrentIndex(self.__sampleCombo.currentIndex() - 1)

    @pyqtSlot()
    def __on_next_button_clicked(self):
        self.__sampleCombo.setCurrentIndex(self.__sampleCombo.currentIndex() + 1)
    
    @pyqtSlot(int)
    def __update_zijder(self, index: int):
        s = QSettings()

        # Set buttons
        if index == 0: # no more going left
            self.__prevButton.setDisabled(True)
        elif index == self.__sampleCombo.count()-1:
            self.__nextButton.setDisabled(True)
        else:
            self.__prevButton.setEnabled(True)
            self.__nextButton.setEnabled(True)

        # Update figure
        current_sample = self.__sampleCombo.currentText()
        current_data = self.__data.get_data(current_sample)
        xh = s.value("Zijder/xh", "N")
        xv = s.value("Zijder/xv", "N")
        y = s.value("Zijder/y", "W")
        z = s.value("Zijder/z", "Up")

        self.__zijder_figure = zijder_plot(
            current_sample, 
            current_data,
            xh, xv, y, z,
            pca_results = self.__results[self.__sampleCombo.currentIndex()], 
            pca_steps = self.__data.get_steps(), 
            pca_anno = self.__anno,
            pca_points = self.__mark,
            pca_lines = self.__line,
            figure = self.__zijder_figure
        )
        self.__zijder_canvas.draw()
        QCoreApplication.processEvents()

    def __update_sequence(self):
        self.__sequence_figure.clf()
        self.__sequence_figure = sequence_plot("", self.__results, dpi = 72, figure = self.__sequence_figure)
        self.__sequence_canvas.draw()
        QCoreApplication.processEvents()

    @pyqtSlot()
    def __export_data(self):
        # Get file name
        __filter = "CSV file (*.csv)"

        try:
            import xlsxwriter
        except ModuleNotFoundError:
            pass
        if "xlsxwriter" in sys.modules:
            __filter += ";;Excel file (*.xlsx)"

        fileout = QFileDialog.getSaveFileName(self, "Save PCA results", "", __filter)[0]
        header = "SampleID/Depth,NRM ({0}),Inclination (°),Declination (°),MADp (°),MADo (°),Min. step,Max. step".format(self.__nrm_unit)

        # Check file extension, set to csv if none was given
        if len(fileout.split(".")) == 1: # Not extension provided
            fileout += ".csv"

        # Save file
        if fileout.split(".")[1] == "csv":
            np.savetxt(fileout, self.__results, delimiter = ",", header = header)
        else:            
            workbook = xlsxwriter.Workbook(fileout)
            worksheet = workbook.add_worksheet()

            worksheet.write(0, 0, "SampleID/Depth")
            worksheet.write(0, 1, "NRM {0}".format(self.__nrm_unit))
            worksheet.write(0, 2, "Inclination (°)")
            worksheet.write(0, 3, "Declination (°)")
            worksheet.write(0, 4, "MADp (°)")
            worksheet.write(0, 5, "MADo (°)")
            worksheet.write(0, 6, "Min. Step")
            worksheet.write(0, 7, "Max. Step")

            row = 1
            for S, N, I, D, Mp, Mo, MiS, MaS in self.__results:
                worksheet.write(row, 0, S)
                worksheet.write(row, 1, N)
                worksheet.write(row, 2, I)
                worksheet.write(row, 3, D)
                worksheet.write(row, 4, Mp)
                worksheet.write(row, 5, Mo)
                worksheet.write(row, 6, MiS)
                worksheet.write(row, 7, MaS)
                row += 1
            
            workbook.close()

    @pyqtSlot()
    def __export_zijder(self):
        from palaeopca.P1Gui.P1ExportDialogs import P1ZijderExport

        dlg = P1ZijderExport(self)
        dlg.setWindowIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("chart-line", "solid"))

        if dlg.exec_() == QDialog.Accepted:
            pbar = P1ProgressBar(self)
            pbar.progress.setValue(0)

            from palaeopca.P1Mpl.P1Zijder import zijder_save

            outdir = dlg.pathPicker.getPath()
            if outdir == "":
                return
            indata = self.__data
            xh = dlg.xhCombo.currentText()
            xv = dlg.xvCombo.currentText()
            y = dlg.yCombo.currentText()
            z = dlg.zCombo.currentText()
            figsize = (float(dlg.figure_width.text()), float(dlg.figure_height.text()))
            fmt = dlg.formatCombo.currentText()
            dpi = float(dlg.figure_dpi.text())

            kwargs = {}

            kwargs["pca_results"] = self.__results
            kwargs["pca_points"] = dlg.markCheck.isChecked()
            kwargs["pca_anno"] = dlg.annoCheck.isChecked()
            kwargs["pca_lines"] = dlg.lineCheck.isChecked()

            zijder_save(outdir, indata, xh, xv, y, z, pbar = pbar, figsize = figsize, fmt = fmt, dpi = dpi, **kwargs)

            pbar.progress.setValue(100)
            pbar.close()

    @pyqtSlot()
    def __export_sequence(self):
        from palaeopca.P1Gui.P1ExportDialogs import P1SequenceExport

        dlg = P1SequenceExport(self)
        dlg.setWindowIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("chart-bar", "solid"))

        if dlg.exec_() == QDialog.Accepted:
            outfile = dlg.pathPicker.getPath()
            if outfile == "":
                return
            if len(outfile.split(".")) == 1: # Not extension provided
                outfile += ".{0}".format(dlg.formatCombo.currentText())
            
            kwargs = {
                "figsize": (float(dlg.figure_width.text()), float(dlg.figure_height.text())),
                "dpi": float(dlg.figure_dpi.text()),
                "NRM_unit": dlg.nrmLine.text(),
                "NRM": dlg.nrmCheck.isChecked(),
                "Incl": dlg.incCheck.isChecked(),
                "Decl": dlg.decCheck.isChecked(),
                "MADp": dlg.madpCheck.isChecked(),
                "MADo": dlg.madoCheck.isChecked(),
                "invertY": dlg.invCheck.isChecked(),
                "ylabel": dlg.yLine.text()
            }

            indata = self.__results

            from palaeopca.P1Mpl.P1Sequence import sequence_plot
            sequence_plot(outfile, indata, True, **kwargs)  
