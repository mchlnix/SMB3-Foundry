
from PySide2.QtWidgets import QFrame


# taken from https://stackoverflow.com/a/41068447/4252230
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)