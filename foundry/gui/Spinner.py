from PySide2.QtWidgets import QSpinBox


class Spinner(QSpinBox):
    def __init__(self, parent, maximum, *, base=16, minimum=0):
        super(Spinner, self).__init__(parent)

        self.setMinimum(minimum)
        self.setMaximum(maximum)

        self.setDisplayIntegerBase(base)

        if base == 16:
            self.setPrefix("0x")
