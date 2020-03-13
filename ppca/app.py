# Standard library
import sys
import os

# Qt
from PyQt5.QtCore import QSettings, QStandardPaths
from PyQt5.QtWidgets import QApplication

# ppca
import ppca
from ppca.P1Gui import P1MainWindow
from ppca.P1Backend import P1Backend


def run():
    global pApp
    pApp.setOrganizationName("W-Soft")
    pApp.setApplicationName("PPCA")
    pApp.setApplicationVersion(ppca.__version__)

    # check if settings for app exist
    s = QSettings()
    
    if not s.contains("Version"):
        s.setValue("Version", ppca.__version__)
        s.setValue("Recent", "")
    if not "Params" in s.childGroups():
        s.beginGroup("Params")
        s.setValue("Volume", 10)
        s.endGroup()
    if not "Import" in s.childGroups():
        s.beginGroup("Import")
        s.setValue("SkipHeader", 1)
        s.setValue("SkipFooter", 0)
        s.setValue("Numerics", ".")
        s.setValue("Separator", ",")
        s.setValue("SkipWhitespaces", "False")
        s.endGroup()
    if not "Units" in s.childGroups():
        s.beginGroup("Units")
        s.setValue("Input", "emu")
        s.setValue("Output", "A/m")
        s.endGroup()
    if not "Zijder" in s.childGroups():
        s.beginGroup("Zijder")
        s.setValue("Style", "./ppca/P1Mpl/styles/zijder.mplstyle")
        s.setValue("xh", "N")
        s.setValue("xv", "N")
        s.setValue("y", "W")
        s.setValue("z", "Up")
        s.setValue("Size", "(5, 5)")
        s.setValue("dpi", 300)
        s.setValue("fmt", "png")
        s.setValue("mark", "False")
        s.setValue("anno", "False")
        s.setValue("line", "False")
        s.endGroup()
    if not "Sequence" in s.childGroups():
        s.beginGroup("Sequence")
        s.setValue("Style", "./ppca/P1Mpl/styles/sequence.mplstyle")
        s.setValue("Size", "(5, 5)")
        s.setValue("dpi", 300)
        s.setValue("fmt", "png")
        s.setValue("NRM", "True")
        s.setValue("Incl", "True")
        s.setValue("Decl", "True")
        s.setValue("MADp", "True")
        s.setValue("MADo", "True")
        s.setValue("invertY", "True")
        s.endGroup()
    if not "Mesh" in s.childGroups():
        s.beginGroup("Mesh")

        s.setValue("Style", "./ppca/P1Mpl/styles/sequence.mplstyle")
        s.setValue("Size", "(5, 5)")
        s.setValue("dpi", 300)
        s.setValue("fmt", "png")

        s.setValue("NRM", "True")
        s.setValue("Incl", "True")
        s.setValue("Decl", "True")
        s.setValue("MADp", "True")
        s.setValue("MADo", "True")

        s.setValue("invertY", "True")
        s.setValue("NRMcmp", "tab20c")
        s.setValue("INCcmp", "PRGn")
        s.setValue("DECcmp", "PRGn")
        s.setValue("MADpcmp", "hot")
        s.setValue("MADocmp", "hot")
        
        s.endGroup()

    mw = P1MainWindow.P1MainWindow()
    mw.show()
    pApp.setActiveWindow(mw)

    return pApp.exec_()


class PPCAApp(QApplication):
    def __init__(self):
        """
        Constructor
        """
        qt_args = [sys.argv[0]]
        super().__init__(qt_args)

        self.__objectRegistry = {}
        self.__widgetRegistry= {}

    def registerWidget(self, item, widget):
        pass

    def registerObject(self, name, object_reference):
        """
        Public method to register an object in the object registry

        :param name: name under which the object is registered (str)
        :param object_reference: reference to the object
        """
        if name in self.__objectRegistry:
            raise KeyError('An object with the name "{0}" is already registered'.format(name))
        else:
            self.__objectRegistry[name] = object_reference

    def removeObject(self, name):
        if name in self.__objectRegistry:
            del self.__objectRegistry[name]
        else:
            raise KeyError('An object with the name "{0}" is not registered'.format(name))


    def getObject(self, name):
        """
        Public method to get a reference to a registered object

        :param name: name under which the object is registered (str)
        :return: reference to registered object
        """
        if name in self.__objectRegistry:
            return self.__objectRegistry[name]
        else:
            raise KeyError('An object with the name "{0}" is not registered.'.format(name))

    def exit(self, status):
        super().exit(status)


pApp = PPCAApp()