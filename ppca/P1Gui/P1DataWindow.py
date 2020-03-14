# Qt
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot, QSettings
from PyQt5.QtWidgets import QWidget, QGridLayout, QTableView, QMenuBar, QMenu, QToolButton, QComboBox, QAction, QDialog, QMdiSubWindow, QSplitter

# Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ppca
from ppca.P1Backend.P1DataObject import P1DataObject
from ppca.P1Backend.P1Backend import P1Backend
from ppca.P1Gui.P1DataModel import P1DataModel
from ppca.P1Mpl.P1Zijder import zijder_plot
from ppca.P1Gui.P1PCAWindow import P1PCAWindow
from ppca.P1Gui.P1MeshWindow import P1MeshWindow
from ppca.P1Gui.P1ProgressBar import P1ProgressBar
import ppca.P1Utils.P1PixmapCache


class P1DataWindow(QWidget):
    def __init__(self, parent = None):
        super(P1DataWindow, self).__init__(parent)

        self.__setupGui()
        self.__connectGui()

    def __setupGui(self):
        self.__layout = QGridLayout(self)
        self.__splitter = QSplitter(Qt.Horizontal, self)

        self.__table = QTableView(self.__splitter)
        self.__model = None

        self.__figure_widget = QWidget(self.__splitter)
        self.__figure_layout = QGridLayout(self.__figure_widget)
        self.__setupMenu()
        
        self.__figure = Figure(figsize = (4, 4), dpi = 150)
        self.__canvas = FigureCanvasQTAgg(self.__figure)
        self.__toolbar = NavigationToolbar2QT(self.__canvas, self.__figure_widget)

        self.__prevButton = QToolButton(self.__figure_widget)
        self.__prevButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.__prevButton.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("chevron-left", "solid"))

        self.__sampleCombo = QComboBox(self.__figure_widget)

        self.__nextButton = QToolButton(self.__figure_widget)
        self.__nextButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.__nextButton.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("chevron-right", "solid"))

        self.__figure_layout.addWidget(self.__toolbar, 0, 0, 1, 1)
        self.__figure_layout.addWidget(self.__prevButton, 0, 1, 1, 1)
        self.__figure_layout.addWidget(self.__sampleCombo, 0, 2, 1, 1)
        self.__figure_layout.addWidget(self.__nextButton, 0, 3, 1, 1)
        self.__figure_layout.addWidget(self.__canvas, 1, 0, 1, 4)
        self.__figure_layout.setRowStretch(1, 10)

        self.__layout.addWidget(self.__splitter)

    def __setupMenu(self):
        self.__menu = QMenuBar()

        self.__fileMenu = QMenu("File")

        #self.__action_convert = QAction(self)
        #self.__action_convert.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("sync-alt", "solid"))
        #self.__action_convert.setText("Convert Units")

        self.__action_close = QAction(self)
        self.__action_close.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("sign-out-alt", "solid"))
        self.__action_close.setText("Close")

        #self.__fileMenu.addAction(self.__action_convert)
        #self.__fileMenu.addSeparator()
        self.__fileMenu.addAction(self.__action_close)

        self.__pcaMenu = QMenu("PCA")

        self.__action_single_interval_pca = QAction(self)
        self.__action_single_interval_pca.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("grip-lines-vertical", "solid"))
        self.__action_single_interval_pca.setText("Single Interval")

        self.__action_best_fit_pca = QAction(self)
        self.__action_best_fit_pca.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("sort-amount-down", "solid"))
        self.__action_best_fit_pca.setText("Best fit")

        self.__action_mesh_pca = QAction(self)
        self.__action_mesh_pca.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("grip-vertical", "solid"))
        self.__action_mesh_pca.setText("Mesh")

        self.__pcaMenu.addAction(self.__action_single_interval_pca)
        self.__pcaMenu.addAction(self.__action_best_fit_pca)
        self.__pcaMenu.addAction(self.__action_mesh_pca)

        self.__exportMenu = QMenu("Export")

        self.__action_export_zijder = QAction(self)
        self.__action_export_zijder.setText("Export Zijderveld plots")
        self.__action_export_zijder.setIcon(ppca.P1Utils.P1PixmapCache.getIcon("chart-line", "solid"))

        self.__exportMenu.addAction(self.__action_export_zijder)

        self.__menu.addMenu(self.__fileMenu)
        self.__menu.addMenu(self.__pcaMenu)
        self.__menu.addMenu(self.__exportMenu)

        self.__layout.setMenuBar(self.__menu)

    def __connectGui(self):
        self.__action_close.triggered.connect(self.parent().close)
        self.__sampleCombo.currentIndexChanged.connect(self.__updateFigure)
        self.__prevButton.clicked.connect(self.__on_prev_button_clicked)
        self.__nextButton.clicked.connect(self.__on_next_button_clicked)

        self.__action_single_interval_pca.triggered.connect(self.__on_single_interval)
        self.__action_best_fit_pca.triggered.connect(self.__on_best_fit)
        self.__action_mesh_pca.triggered.connect(self.__on_mesh)

        self.__action_export_zijder.triggered.connect(self.__export_zijder)
    
    def set_data(self, data: P1DataObject):
        self.__data = data
        self.__model = P1DataModel(data, ["SampleID/Depth", "Steps", "x", "y", "z"])
        self.__table.setModel(self.__model)
        self.__sampleCombo.currentIndexChanged.disconnect(self.__updateFigure)
        self.__sampleCombo.clear()
        self.__sampleCombo.addItems([str(x) for x in self.__data.get_samples().tolist()])
        self.__sampleCombo.currentIndexChanged.connect(self.__updateFigure)
        self.__updateFigure(0)

    @pyqtSlot()
    def __on_single_interval(self):
        from ppca.P1Gui.P1PCADialogs import P1SingleIntervalDialog
        dlg = P1SingleIntervalDialog([str(x) for x in self.__data.get_steps()], self)
        dlg.setWindowIcon(ppca.P1Utils.P1PixmapCache.getIcon("grip-lines-vertical", "solid"))
        if dlg.exec_() == QDialog.Accepted:
            pbar = P1ProgressBar(self)
            pbar.progress.setValue(0)

            p = P1Backend()
            p.set_data(self.__data)
            pca = p.run_single_interval(float(dlg.minCombo.currentText()), float(dlg.maxCombo.currentText()), dlg.NRMUnitCombo.currentText(), pbar = pbar)
            pbar.progress.setValue(100)
            pbar.close()

            subwindow = QMdiSubWindow(self.parent().mdiArea())
            subwindow.setWindowTitle("PCA Results Single Interval - {0}".format(self.parent().windowTitle().split("-")[1]))
            subwindow.setWindowIcon(ppca.P1Utils.P1PixmapCache.getIcon("grip-lines-vertical", "solid"))
            subwindow.setWidget(P1PCAWindow(subwindow))
            subwindow.setAttribute(Qt.WA_DeleteOnClose)
            subwindow.widget().set_data(self.__data, pca, dlg.NRMUnitCombo.currentText())
            subwindow.show()

    @pyqtSlot()
    def __on_best_fit(self):
        from ppca.P1Gui.P1PCADialogs import P1BestFitDialog
        dlg = P1BestFitDialog([str(x) for x in self.__data.get_steps()], self)
        dlg.setWindowIcon(ppca.P1Utils.P1PixmapCache.getIcon("sort-amount-down", "solid"))
        if dlg.exec_() == QDialog.Accepted:
            pbar = P1ProgressBar(self)
            pbar.progress.setValue(0)

            p = P1Backend()
            p.set_data(self.__data)
            pca = p.run_best_fit(dlg.minSpin.value(), dlg.NRMUnitCombo.currentText(), pbar = pbar)
            pbar.progress.setValue(100)
            pbar.close()
            
            subwindow = QMdiSubWindow(self.parent().mdiArea())
            subwindow.setWindowTitle("PCA Results Best Fit - {0}".format(self.parent().windowTitle().split("-")[1]))
            subwindow.setWindowIcon(ppca.P1Utils.P1PixmapCache.getIcon("sort-amount-down", "solid"))
            subwindow.setWidget(P1PCAWindow(subwindow))
            subwindow.setAttribute(Qt.WA_DeleteOnClose)
            subwindow.widget().set_data(self.__data, pca)
            subwindow.show()

    @pyqtSlot()
    def __on_mesh(self):
        from ppca.P1Gui.P1PCADialogs import P1MeshDialog
        dlg = P1MeshDialog([str(x) for x in self.__data.get_steps()], self)
        dlg.setWindowIcon(ppca.P1Utils.P1PixmapCache.getIcon("grip-vertical", "solid"))
        if dlg.exec_() == QDialog.Accepted:
            pbar = P1ProgressBar(self)
            pbar.progress.setValue(0)

            p = P1Backend()
            p.set_data(self.__data)
            pca = p.run_mesh(window = dlg.stepSpin.value(), pbar = pbar)
            pbar.progress.setValue(100)
            pbar.close()

            subwindow = QMdiSubWindow(self.parent().mdiArea())
            subwindow.setWindowTitle("PCA Results Mesh - {0}".format(self.parent().windowTitle().split("-")[1]))
            subwindow.setWindowIcon(ppca.P1Utils.P1PixmapCache.getIcon("grip-vertical", "solid"))
            subwindow.setWidget(P1MeshWindow(subwindow))
            subwindow.setAttribute(Qt.WA_DeleteOnClose)
            subwindow.widget().set_data(pca)
            #self.parent().mdiArea().addSubWindow(subwindow)
            subwindow.show()

    @pyqtSlot()
    def __on_prev_button_clicked(self):
        self.__sampleCombo.setCurrentIndex(self.__sampleCombo.currentIndex() - 1)

    @pyqtSlot()
    def __on_next_button_clicked(self):
        self.__sampleCombo.setCurrentIndex(self.__sampleCombo.currentIndex() + 1)
    
    @pyqtSlot()
    def __updateFigure(self, index: int):
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
        self.__figure = zijder_plot(current_sample, current_data, xh, xv, y, z, figure = self.__figure, units = self.__data.get_units())
        self.__canvas.draw()

        QCoreApplication.processEvents()

    @pyqtSlot()
    def __export_zijder(self):
        from ppca.P1Gui.P1ExportDialogs import P1ZijderExport

        dlg = P1ZijderExport(self)
        dlg.setWindowIcon(ppca.P1Utils.P1PixmapCache.getIcon("chart-line", "solid"))
        dlg.PCABox.setDisabled(True)
        dlg.markCheck.setChecked(False)
        dlg.annoCheck.setChecked(False)
        dlg.lineCheck.setChecked(False)

        if dlg.exec_() == QDialog.Accepted:
            pbar = P1ProgressBar(self)
            pbar.progress.setValue(0)

            from ppca.P1Mpl.P1Zijder import zijder_save

            outdir = dlg.pathPicker.getPath()
            indata = self.__data
            xh = dlg.xhCombo.currentText()
            xv = dlg.xvCombo.currentText()
            y = dlg.yCombo.currentText()
            z = dlg.zCombo.currentText()
            figsize = (float(dlg.figure_width.text()), float(dlg.figure_height.text()))
            fmt = dlg.formatCombo.currentText()
            dpi = float(dlg.figure_dpi.text())

            zijder_save(outdir, indata, xh, xv, y, z, pbar = pbar, figsize = figsize, fmt = fmt, dpi = dpi)

            pbar.progress.setValue(100)
            pbar.close()
        