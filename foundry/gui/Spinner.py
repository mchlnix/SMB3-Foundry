from PySide2.QtWidgets import QSpinBox

SPINNER_MAX_VALUE = 0xFF_FF_FF  # arbitrary; 16,7 MB


class HexSpinner(QSpinBox):
    def __init__(self, parent, maximum=SPINNER_MAX_VALUE):
        super(HexSpinner, self).__init__(parent)

        self.setRange(0, maximum)
        self.setDisplayIntegerBase(16)

        self.setPrefix("0x")
