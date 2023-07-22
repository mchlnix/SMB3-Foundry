from PySide6.QtWidgets import QFrame


# taken from https://stackoverflow.com/a/41068447/4252230
class HorizontalLine(QFrame):
    def __init__(self):
        super(HorizontalLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
