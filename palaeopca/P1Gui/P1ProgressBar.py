from PyQt5.QtWidgets import QDialog, QProgressBar


class P1ProgressBar(QDialog):
    def __init__(self, parent = None):
        super(P1ProgressBar, self).__init__(parent)
        self.__setupGui()

    def __setupGui(self):
        self.setWindowTitle("Processing ...")
        self.progress = QProgressBar(self)
        self.progress.setGeometry(0, 0, 300, 25)
        self.progress.setMaximum(100)
        self.show()
