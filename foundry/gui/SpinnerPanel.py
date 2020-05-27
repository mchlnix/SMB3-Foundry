from typing import Optional

from PySide2.QtCore import Signal, SignalInstance
from PySide2.QtWidgets import QFormLayout, QSizePolicy, QWidget

from foundry.game.gfx.objects.LevelObjectController import LevelObjectController
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
        spinner_layout.addRow("Type:", self.spin_type)
        spinner_layout.addRow("Length:", self.spin_length)

        self.setLayout(spinner_layout)

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

        self.enable_domain(isinstance(obj, LevelObjectController), obj.domain)

        if isinstance(obj, LevelObjectController) and obj.is_4byte:
            self.set_length(obj.length)
        else:
            self.enable_length(False)

        self.blockSignals(False)

        print(obj.properties())
        print(self.get_type(), self.get_domain(), self.get_length())

    def get_type(self):
        return self.spin_type.value()

    def set_type(self, object_type: int):
        assert object_type is not None
        self.spin_type.setValue(object_type)
        self.spin_type.setEnabled(True)

    def get_domain(self):
        return self.spin_domain.value()

    def set_domain(self, domain: int):
        assert domain is not None
        self.spin_domain.setValue(domain)
        self.spin_domain.setEnabled(True)

    def get_length(self) -> int:
        return self.spin_length.value()

    def set_length(self, length: int):
        assert length is not None
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
