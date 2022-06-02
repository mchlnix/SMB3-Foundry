from PySide6.QtWidgets import QSpinBox

SPINNER_MAX_VALUE = 0xFF_FF_FF  # arbitrary; 16,7 MB


class Spinner(QSpinBox):
    def __init__(self, parent, maximum=SPINNER_MAX_VALUE, base=16):
        super(Spinner, self).__init__(parent)

        self.setRange(0, maximum)
        self.setDisplayIntegerBase(base)

        if base == 16:
            self.setPrefix("0x")
