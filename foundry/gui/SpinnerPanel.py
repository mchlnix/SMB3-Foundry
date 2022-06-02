from typing import Optional

from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtWidgets import QFormLayout, QSizePolicy, QWidget

from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.game.gfx.objects.ObjectLike import ObjectLike
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.Spinner import Spinner

MAX_DOMAIN = 0x07
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF


class SpinnerPanel(QWidget):
    object_change: SignalInstance = Signal(int)

    zoom_in_triggered: SignalInstance = Signal()
    zoom_out_triggered: SignalInstance = Signal()

    def __init__(self, parent: Optional[QWidget], level_ref: LevelRef):
        super(SpinnerPanel, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.level_ref = level_ref
        self.level_ref.data_changed.connect(self.update)

        self.spin_domain = Spinner(self, maximum=MAX_DOMAIN)
        self.spin_domain.setEnabled(False)
        self.spin_domain.valueChanged.connect(self.object_change.emit)

        self.spin_type = Spinner(self, maximum=MAX_TYPE)
        self.spin_type.setEnabled(False)
        self.spin_type.valueChanged.connect(self.object_change.emit)

        self.spin_length = Spinner(self, maximum=MAX_LENGTH)
        self.spin_length.setEnabled(False)
        self.spin_length.valueChanged.connect(self.object_change.emit)

        spinner_layout = QFormLayout()
        spinner_layout.addRow("Bank/Domain:", self.spin_domain)
        spinner_layout.addRow("Index:", self.spin_type)
        spinner_layout.addRow("Length:", self.spin_length)

        self.setLayout(spinner_layout)

        self.setWhatsThis(
            "<b>Spinner Panel</b><br/>"
            "The Spinner Panel gives raw byte access to objects for advanced users. The values are shown "
            "in hexadecimal notation.<br/>"
            "Level objects and enemies/items are categorized using domains and indexes. Which domain an "
            "object is in, doesn't hold much information about the object, if at all.<br/>"
            "As for the index, the only important information is, that all objects from 0x00 - 0x0F can "
            "not be resized. "
            "They have fixed dimensions, like the background bushes in Level 1-1.<br/>"
            "All other objects have 16 different iterations, meaning 0x10 - 0x1F, for example, is one "
            "object, with 16 different sizes, going from smallest to largest. In what way these objects "
            "expand, depends on their particular expansion type.<br/>"
            "Some '4-byte' objects can expand in a second way, since they have an additional byte "
            "holding that information. For example a platform, which can be sized vertically using the "
            "index and horizontally using the 4th byte."
        )

    def update(self):
        if len(self.level_ref.selected_objects) == 1:
            selected_object = self.level_ref.selected_objects[0]

            if isinstance(selected_object, ObjectLike):
                self._populate_spinners(selected_object)

        else:
            self.disable_all()

        super(SpinnerPanel, self).update()

    def _populate_spinners(self, obj: ObjectLike):
        self.blockSignals(True)

        self.set_type(obj.obj_index)

        self.enable_domain(isinstance(obj, LevelObject), obj.domain)

        if isinstance(obj, LevelObject) and obj.is_4byte:
            self.set_length(obj.length)
        else:
            self.enable_length(False)

        self.blockSignals(False)

    def get_type(self):
        return self.spin_type.value()

    def set_type(self, object_type: int):
        self.spin_type.setValue(object_type)
        self.spin_type.setEnabled(True)

    def get_domain(self):
        return self.spin_domain.value()

    def set_domain(self, domain: int):
        self.spin_domain.setValue(domain)
        self.spin_domain.setEnabled(True)

    def get_length(self) -> int:
        return self.spin_length.value()

    def set_length(self, length: int):
        self.spin_length.setValue(length)
        self.spin_length.setEnabled(True)

    def enable_type(self, enable: bool, value: int = 0):
        self.spin_type.setValue(value)
        self.spin_type.setEnabled(enable)

    def enable_domain(self, enable: bool, value: int = 0):
        self.spin_domain.setValue(value)
        self.spin_domain.setEnabled(enable)

    def enable_length(self, enable: bool, value: int = 0):
        self.spin_length.setValue(value)
        self.spin_length.setEnabled(enable)

    def clear_spinners(self):
        self.set_type(0x00)
        self.set_domain(0x00)
        self.set_length(0x00)

    def disable_all(self):
        self.blockSignals(True)

        self.clear_spinners()

        self.enable_type(False)
        self.enable_domain(False)
        self.enable_length(False)

        self.blockSignals(False)
