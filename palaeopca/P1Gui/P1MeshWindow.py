# Standard library
import sys
import os
from typing import Dict

# Qt
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot
from PyQt5.QtWidgets import QWidget, \
    QGridLayout, \
    QTableView, \
    QMenuBar, \
    QMenu, \
    QToolButton, \
    QComboBox, \
    QAction, \
    QTabWidget, \
    QVBoxLayout, \
    QMessageBox, \
    QFileDialog, \
    QDialog


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
from palaeopca.P1Mpl.P1Mesh import mesh_plot
import palaeopca.P1Utils.P1PixmapCache


class P1MeshWindow(QWidget):
    def __init__(self, parent = None):
        super(P1MeshWindow, self).__init__(parent)

        self.__setupGui()
        self.__connectGui()

    def __setupGui(self):
        self.__layout = QGridLayout(self)
        self.__setupMenu()

        self.__M_table = QTableView()
        self.__M_model = None

        self.__Inc_table = QTableView()
        self.__Inc_model = None

        self.__Dec_table = QTableView()
        self.__Dec_model = None

        self.__MADp_table = QTableView()
        self.__MADp_model = None

        self.__MADo_table = QTableView()
        self.__MADo_model = None
        
        self.__figure_widget = QWidget()
        self.__figure_widget.setLayout(QVBoxLayout())
        self.__figure = Figure(figsize = (7, 5), dpi = 150)
        self.__canvas = FigureCanvasQTAgg(self.__figure)
        self.__toolbar = NavigationToolbar2QT(self.__canvas, self.__figure_widget)
        self.__figure_widget.layout().addWidget(self.__toolbar)
        self.__figure_widget.layout().addWidget(self.__canvas)

        self.__tabs = QTabWidget()
        self.__tabs.addTab(self.__M_table, "Magnetization")
        self.__tabs.addTab(self.__Inc_table, "Inclination")
        self.__tabs.addTab(self.__Dec_table, "Declination")
        self.__tabs.addTab(self.__MADp_table, "MADp")
        self.__tabs.addTab(self.__MADo_table, "MADo")
        self.__tabs.addTab(self.__figure_widget, "Mesh Plot")

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

        self.__action_export_mesh = QAction(self)
        self.__action_export_mesh.setIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("chart-area", "solid"))
        self.__action_export_mesh.setText("Export mesh plot")

        self.__exportMenu.addAction(self.__action_export_data)
        self.__exportMenu.addAction(self.__action_export_mesh)

        self.__menu.addMenu(self.__fileMenu)
        self.__menu.addMenu(self.__exportMenu)

        self.__layout.setMenuBar(self.__menu)

    def __connectGui(self):
        self.__action_close.triggered.connect(self.parent().close)
        self.__action_export_data.triggered.connect(self.__export_data)
        self.__action_export_mesh.triggered.connect(self.__export_mesh)
    
    def set_data(self, data: Dict):
        self.__data = data

        self.__M_model = P1ResultsModel(self.__data["M"], [str(x) for x in self.__data["Steps"].tolist()])
        self.__M_table.setModel(self.__M_model)

        self.__Inc_model = P1ResultsModel(self.__data["Inclination"], [str(x) for x in self.__data["Centers"].tolist()])
        self.__Inc_table.setModel(self.__Inc_model)

        self.__Dec_model = P1ResultsModel(self.__data["Declination"], [str(x) for x in self.__data["Centers"].tolist()])
        self.__Dec_table.setModel(self.__Dec_model)

        self.__MADp_model = P1ResultsModel(self.__data["MADp"], [str(x) for x in self.__data["Centers"].tolist()])
        self.__MADp_table.setModel(self.__MADp_model)

        self.__MADo_model = P1ResultsModel(self.__data["MADo"], [str(x) for x in self.__data["Centers"].tolist()])
        self.__MADo_table.setModel(self.__MADo_model)

        self.__update_mesh()

    def __update_mesh(self):
        self.__figure.clf()
        self.__figure = mesh_plot("", self.__data, figure = self.__figure)
        self.__canvas.draw()
        QCoreApplication.processEvents()

    @pyqtSlot()
    def __export_data(self):
        """
        Samples: vector of SampleID/Depth.
        Centers: vector of window centers.
        Steps: vector of all steps.
        M: Magnetization matrix with observations in rows, windows in columns.
        Inclination: Inclination matrix with observations in rows, windows in columns.
        Declination: Declination matrix with observations in rows, windows in columns.
        MADp: medium angular deviation, prolate matrix with observations in rows, windows in columns.
        MADo: medium angular deviation, oblate matrix with observations in rows, windows in columns.
        """
        from palaeopca.P1Gui.P1ExportDialogs import P1MeshDataExport

        dlg = P1MeshDataExport(self)
        dlg.setWindowIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("grip-vertical", "solid"))

        if dlg.exec_() == QDialog.Accepted:
            # Determine file extension
            ind = dlg.fmtCombo.currentIndex()
            fmt = "csv" if ind == 0 else "xlsx"

            # NRM
            if dlg.nrmCheck.isChecked():
                fileout = os.path.join(dlg.pathPicker.getPath(), "Magnetization_Mesh_{0}.{1}".format(len(self.__data["Centers"]), fmt))
                if fmt == "csv":
                    # Make header
                    if dlg.stepCheck.isChecked():
                        header = "," + ",".join([str(x) for x in self.__data["Steps"]])
                    else:
                        header = ""
                    
                    # Prepare data and add vectors if desired
                    data = self.__data["M"]
                    if dlg.sampleCheck.isChecked():
                        data = np.insert(data, 0, values = self.__data["Samples"], axis = 1)

                    try:                    
                        np.savetxt(fileout, data, delimiter = ",", header = header)
                    except PermissionError:
                        err = QMessageBox(self)
                        err.setText("Cannot open file for writing.")
                        err.setInformativeText("Make sure the file is not locked/opened by another program.")
                        err.setDetailedText("Affected file: {0}".format(fileout))
                        err.exec()
                        return

                else:
                    try:
                        import xlsxwriter
                    except ModuleNotFoundError:
                        err = QMessageBox(self)
                        err.setText("Cannot find xlsxwriter module.")
                        err.setInformativeText("Install xlsxwriter module to enable xls(x) export.")
                        err.setDetailedText("Try installing xlsxwriter via pip from the command line: pip install xlsxwriter")
                        err.exec()
                        return
                    
                    workbook = xlsxwriter.Workbook(fileout)
                    worksheet = workbook.add_worksheet()

                    col = 0
                    if dlg.sampleCheck.isChecked():
                        worksheet.write(0, col, "SampleID/Depth")
                        for row, s in enumerate(self.__data["Samples"]):
                            worksheet.write(row + 1, col, s)
                        col += 1
                    
                    for c, step in enumerate(self.__data["Steps"]):
                        worksheet.write(0, c + col, str(step))

                    row = 1
                    for m in self.__data["M"]:
                        for c in range(col, len(m) + col):
                            worksheet.write(row, c, m[c - col])
                        row += 1
                    
                    workbook.close()

            # Inclination
            if dlg.incCheck.isChecked():
                fileout = os.path.join(dlg.pathPicker.getPath(), "Inclination_Mesh_{0}.{1}".format(len(self.__data["Centers"]), fmt))
                if fmt == "csv":
                    # Make header
                    if dlg.stepCheck.isChecked():
                        header = "," + ",".join([str(x) for x in self.__data["Centers"]])
                    else:
                        header = ""
                    
                    # Prepare data and add vectors if desired
                    data = self.__data["Inclination"]
                    if dlg.sampleCheck.isChecked():
                        data = np.insert(data, 0, values = self.__data["Samples"], axis = 1)

                    try:                    
                        np.savetxt(fileout, data, delimiter = ",", header = header)
                    except PermissionError:
                        err = QMessageBox(self)
                        err.setText("Cannot open file for writing.")
                        err.setInformativeText("Make sure the file is not locked/opened by another program.")
                        err.setDetailedText("Affected file: {0}".format(fileout))
                        err.exec()
                        return

                else:
                    try:
                        import xlsxwriter
                    except ModuleNotFoundError:
                        err = QMessageBox(self)
                        err.setText("Cannot find xlsxwriter module.")
                        err.setInformativeText("Install xlsxwriter module to enable xls(x) export.")
                        err.setDetailedText("Try installing xlsxwriter via pip from the command line: pip install xlsxwriter")
                        err.exec()
                        return
                    
                    workbook = xlsxwriter.Workbook(fileout)
                    worksheet = workbook.add_worksheet()

                    col = 0
                    if dlg.sampleCheck.isChecked():
                        worksheet.write(0, col, "SampleID/Depth")
                        for row, s in enumerate(self.__data["Samples"]):
                            worksheet.write(row + 1, col, s)
                        col += 1
                    
                    for c, center in enumerate(self.__data["Centers"]):
                        worksheet.write(0, c + col, str(center))

                    row = 1
                    for i in self.__data["Inclination"]:
                        for c in range(col, len(i) + col):
                            worksheet.write(row, c, i[c - col])
                        row += 1
                    
                    workbook.close()

            # Declination
            if dlg.decCheck.isChecked():
                fileout = os.path.join(dlg.pathPicker.getPath(), "Declination_Mesh_{0}.{1}".format(len(self.__data["Centers"]), fmt))
                if fmt == "csv":
                    # Make header
                    if dlg.stepCheck.isChecked():
                        header = "," + ",".join([str(x) for x in self.__data["Centers"]])
                    else:
                        header = ""
                    
                    # Prepare data and add vectors if desired
                    data = self.__data["Declination"]
                    if dlg.sampleCheck.isChecked():
                        data = np.insert(data, 0, values = self.__data["Samples"], axis = 1)

                    try:                    
                        np.savetxt(fileout, data, delimiter = ",", header = header)
                    except PermissionError:
                        err = QMessageBox(self)
                        err.setText("Cannot open file for writing.")
                        err.setInformativeText("Make sure the file is not locked/opened by another program.")
                        err.setDetailedText("Affected file: {0}".format(fileout))
                        err.exec()
                        return

                else:
                    try:
                        import xlsxwriter
                    except ModuleNotFoundError:
                        err = QMessageBox(self)
                        err.setText("Cannot find xlsxwriter module.")
                        err.setInformativeText("Install xlsxwriter module to enable xls(x) export.")
                        err.setDetailedText("Try installing xlsxwriter via pip from the command line: pip install xlsxwriter")
                        err.exec()
                        return
                    
                    workbook = xlsxwriter.Workbook(fileout)
                    worksheet = workbook.add_worksheet()

                    col = 0
                    if dlg.sampleCheck.isChecked():
                        worksheet.write(0, col, "SampleID/Depth")
                        for row, s in enumerate(self.__data["Samples"]):
                            worksheet.write(row + 1, col, s)
                        col += 1
                    
                    for c, center in enumerate(self.__data["Centers"]):
                        worksheet.write(0, c + col, str(center))

                    row = 1
                    for d in self.__data["Declination"]:
                        for c in range(col, len(d) + col):
                            worksheet.write(row, c, d[c - col])
                        row += 1
                    
                    workbook.close()

            # MADp
            if dlg.madpCheck.isChecked():
                fileout = os.path.join(dlg.pathPicker.getPath(), "MADp_Mesh_{0}.{1}".format(len(self.__data["Centers"]), fmt))
                if fmt == "csv":
                    # Make header
                    if dlg.stepCheck.isChecked():
                        header = "," + ",".join([str(x) for x in self.__data["Centers"]])
                    else:
                        header = ""
                    
                    # Prepare data and add vectors if desired
                    data = self.__data["MADp"]
                    if dlg.sampleCheck.isChecked():
                        data = np.insert(data, 0, values = self.__data["Samples"], axis = 1)

                    try:                    
                        np.savetxt(fileout, data, delimiter = ",", header = header)
                    except PermissionError:
                        err = QMessageBox(self)
                        err.setText("Cannot open file for writing.")
                        err.setInformativeText("Make sure the file is not locked/opened by another program.")
                        err.setDetailedText("Affected file: {0}".format(fileout))
                        err.exec()
                        return

                else:
                    try:
                        import xlsxwriter
                    except ModuleNotFoundError:
                        err = QMessageBox(self)
                        err.setText("Cannot find xlsxwriter module.")
                        err.setInformativeText("Install xlsxwriter module to enable xls(x) export.")
                        err.setDetailedText("Try installing xlsxwriter via pip from the command line: pip install xlsxwriter")
                        err.exec()
                        return
                    
                    workbook = xlsxwriter.Workbook(fileout)
                    worksheet = workbook.add_worksheet()

                    col = 0
                    if dlg.sampleCheck.isChecked():
                        worksheet.write(0, col, "SampleID/Depth")
                        for row, s in enumerate(self.__data["Samples"]):
                            worksheet.write(row + 1, col, s)
                        col += 1
                    
                    for c, center in enumerate(self.__data["Centers"]):
                        worksheet.write(0, c + col, str(center))

                    row = 1
                    for m in self.__data["MADp"]:
                        for c in range(col, len(m) + col):
                            worksheet.write(row, c, m[c - col])
                        row += 1
                    
                    workbook.close()

            # MADo
            if dlg.madoCheck.isChecked():
                fileout = os.path.join(dlg.pathPicker.getPath(), "MADo_Mesh_{0}.{1}".format(len(self.__data["Centers"]), fmt))
                if fmt == "csv":
                    # Make header
                    if dlg.stepCheck.isChecked():
                        header = "," + ",".join([str(x) for x in self.__data["Centers"]])
                    else:
                        header = ""
                    
                    # Prepare data and add vectors if desired
                    data = self.__data["MADo"]
                    if dlg.sampleCheck.isChecked():
                        data = np.insert(data, 0, values = self.__data["Samples"], axis = 1)

                    try:                    
                        np.savetxt(fileout, data, delimiter = ",", header = header)
                    except PermissionError:
                        err = QMessageBox(self)
                        err.setText("Cannot open file for writing.")
                        err.setInformativeText("Make sure the file is not locked/opened by another program.")
                        err.setDetailedText("Affected file: {0}".format(fileout))
                        err.exec()
                        return

                else:
                    try:
                        import xlsxwriter
                    except ModuleNotFoundError:
                        err = QMessageBox(self)
                        err.setText("Cannot find xlsxwriter module.")
                        err.setInformativeText("Install xlsxwriter module to enable xls(x) export.")
                        err.setDetailedText("Try installing xlsxwriter via pip from the command line: pip install xlsxwriter")
                        err.exec()
                        return
                    
                    workbook = xlsxwriter.Workbook(fileout)
                    worksheet = workbook.add_worksheet()

                    col = 0
                    if dlg.sampleCheck.isChecked():
                        worksheet.write(0, col, "SampleID/Depth")
                        for row, s in enumerate(self.__data["Samples"]):
                            worksheet.write(row + 1, col, s)
                        col += 1
                    
                    for c, center in enumerate(self.__data["Centers"]):
                        worksheet.write(0, c + col, str(center))

                    row = 1
                    for m in self.__data["MADo"]:
                        for c in range(col, len(m) + col):
                            worksheet.write(row, c, m[c - col])
                        row += 1
                    
                    workbook.close()

    @pyqtSlot()
    def __export_mesh(self):
        from palaeopca.P1Gui.P1ExportDialogs import P1MeshExport

        dlg = P1MeshExport(self)
        dlg.setWindowIcon(palaeopca.P1Utils.P1PixmapCache.getIcon("grip-vertical", "solid"))

        if dlg.exec_() == QDialog.Accepted:
            outfile = dlg.pathPicker.getPath()

            kwargs = {
                "figsize": (float(dlg.figure_width.text()), float(dlg.figure_height.text())),
                "dpi": float(dlg.figure_dpi.text()),
                "NRM": dlg.nrmCheck.isChecked(),
                "Incl": dlg.incCheck.isChecked(),
                "Decl": dlg.decCheck.isChecked(),
                "MADp": dlg.madpCheck.isChecked(),
                "MADo": dlg.madoCheck.isChecked(),
                "invertY": dlg.invCheck.isChecked(),
            }

            mesh_plot(outfile, self.__data, save = True, **kwargs)
        
        

    