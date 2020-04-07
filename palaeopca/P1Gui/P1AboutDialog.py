from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel

import palaeopca

class P1AboutDialog(QDialog):
    def __init__(self, parent = None):
        super(P1AboutDialog, self).__init__(parent)
        self.setWindowTitle("About palaeopca")

        self.__layout = QGridLayout(self)

        self.__aboutTitle = QLabel("Palaeopca")
        self.__aboutTitle.setStyleSheet("color: darkblue; font: 15px")
        self.__aboutText = QLabel("""
        {0}

        Version: {1}
        License: {2}
        Author: {3}
        Contact: {4}

        Please cite as:
        Wiers, S., Almqvist, B. (2020). Palaeopca, a Tool 
        to Unlock the full Potential of Principal Component 
        Analysis in Palaeomagnetism. In preparation.
        """.format(palaeopca.__description__, palaeopca.__version__, palaeopca.__license__, palaeopca.__author__, palaeopca.__email__))
        
        self.__layout.addWidget(self.__aboutTitle, 0, 0)
        self.__layout.addWidget(self.__aboutText, 1, 0)
