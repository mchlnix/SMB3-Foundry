from PySide2.QtCore import QRect, QSize, Qt
from PySide2.QtGui import QColor, QPaintEvent, QPainter
from PySide2.QtWidgets import QFormLayout, QSizePolicy, QWidget, QLabel, QFrame

from foundry.game.level.LevelRef import LevelRef


class LevelSizeBar(QWidget):
    def __init__(self, parent, level):
        super(LevelSizeBar, self).__init__(parent)

        self.level: Level = level
        self.level.data_changed.connect(self.update)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.bytes_label = QLabel(self)
        self.bytes_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.bytes_label.setText(self.text)
        self.bytes_label.setMargin(0)
        self.bytes_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        layout = QFormLayout()
        layout.setMargin(0)
        layout.addRow(f"{self.value_description}:", self.bytes_label)

        self.setLayout(layout)

        self.setWhatsThis(
            "<b>Level Size Bar</b><br/>"
            "The objects inside a level, like platforms and item blocks, are stored as bytes in the ROM. "
            "Since levels are stored one after another, saving a level with more objects, than it originally "
            "had, would overwrite another level and probably cause the game to crash, if you would enter it, "
            "while playing.<br/>"
            "This bar shows, how much of the available space for level objects is currently taken up. It will turn "
            "red, when too many level objects have been placed (or if the level objects would result in more bytes, "
            "than the level originally had)."
        )

    def update(self):
        self.setToolTip(f"{self.value_description}: {self.current_value}/{self.original_value} Bytes")
        self.bytes_label.setText(self.text)
        return super(LevelSizeBar, self).update()

    @property
    def value_color(self):
        return QColor.fromRgb(0x58D858)

    @property
    def value_description(self):
        return "Objects"

    @property
    def original_value(self):
        try:
            return self.level.object_size_on_disk
        except TypeError:
            return 0

    @property
    def current_value(self):
        try:
            return self.level.current_object_size()
        except TypeError:
            return 0

    @property
    def text(self):
        return f"{self.current_value} / {self.original_value} Bytes"
