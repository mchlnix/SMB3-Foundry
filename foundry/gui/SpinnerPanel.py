from typing import Union

from PySide2.QtCore import Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QFormLayout, QVBoxLayout

from foundry.game.gfx.objects.LevelObject import LevelObject
from foundry.gui.Events import EVT_UNDO_CLEARED, EVT_UNDO_COMPLETE, EVT_REDO_COMPLETE, EVT_UNDO_SAVED
from foundry.gui.HexSpinner import HexSpinner
from foundry.gui.LevelView import LevelView

ID_SPIN_DOMAIN = 1000
ID_SPIN_TYPE = 1001
ID_SPIN_LENGTH = 1002

ID_TOOL_ZOOM_OUT = 1101
ID_TOOL_ZOOM_IN = 1102

ID_TOOL_UNDO = 1103
ID_TOOL_REDO = 1104

MAX_DOMAIN = 0x07
MAX_TYPE = 0xFF
MAX_LENGTH = 0xFF


class SpinnerPanel(QWidget):
    undo_triggered = Signal()
    redo_triggered = Signal()

    object_change = Signal

    def __init__(self, parent: QWidget, level_view_ref: LevelView):
        super(SpinnerPanel, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.level_view_ref = level_view_ref

        self.undo_button = QPushButton(QIcon("data/icons/rotate-ccw.svg"), "", self)
        self.undo_button.pressed.connect(self.on_undo)
        self.undo_button.setDisabled(True)

        self.redo_button = QPushButton(QIcon("data/icons/rotate-cw.svg"), "", self)
        self.redo_button.pressed.connect(self.on_redo)

        self.zoom_out_button = QPushButton(QIcon("data/icons/zoom-out.svg"), "", self)
        self.zoom_out_button.pressed.connect(self.level_view_ref.zoom_out)

        self.zoom_in_button = QPushButton(QIcon("data/icons/zoom-in.svg"), "", self)
        self.zoom_in_button.pressed.connect(self.level_view_ref.zoom_in)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.undo_button)
        button_layout.addWidget(self.redo_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.zoom_out_button)
        button_layout.addWidget(self.zoom_in_button)

        self.spin_domain = HexSpinner(self, maximum=MAX_DOMAIN)
        self.spin_domain.setEnabled(False)

        self.spin_type = HexSpinner(self, maximum=MAX_TYPE)
        self.spin_type.setEnabled(False)

        self.spin_length = HexSpinner(self, maximum=MAX_LENGTH)
        self.spin_length.setEnabled(False)

        spinner_layout = QFormLayout()
        spinner_layout.addRow("Bank/Domain:", self.spin_domain)
        spinner_layout.addRow("Type:", self.spin_type)
        spinner_layout.addRow("Length:", self.spin_length)

        self.setLayout(QVBoxLayout(self))

        self.layout().addLayout(button_layout)
        self.layout().addLayout(spinner_layout)

    def update(self):
        if len(self.level_view_ref.level.selected_objects) == 1:
            selected_object = self.level_view_ref.level.selected_objects[0]

            if isinstance(selected_object, LevelObject):
                self._populate_spinners(selected_object)

        else:
            self.disable_all()

        super(SpinnerPanel, self).update()

    def _populate_spinners(self, obj: LevelObject):
        self.set_type(obj.type)
        self.set_domain(obj.domain)

        if obj.is_4byte:
            self.set_length(obj.secondary_length)
        else:
            self.enable_length(False)

    def on_undo(self):
        self.enable_redo()

        # todo make events work
        if self.level_view_ref.undo_stack.undo_index - 1 <= 0:
            self.disable_undo()

        self.undo_triggered.emit()

    def on_redo(self):
        self.redo_triggered.emit()

    def disable_buttons(self, event):
        evt_id = event.GetEventType()

        if evt_id == EVT_UNDO_CLEARED.typeId:
            self.disable_undo()
            self.disable_redo()

        elif evt_id == EVT_UNDO_SAVED.typeId:
            self.enable_undo()
            self.disable_redo()

        elif evt_id == EVT_UNDO_COMPLETE.typeId:
            self.enable_redo()
            if not event.undos_left:
                self.disable_undo()

        elif evt_id == EVT_REDO_COMPLETE.typeId:
            self.enable_undo()
            if not event.redos_left:
                self.disable_redo()

    def disable_undo(self):
        self.undo_button.setEnabled(False)

    def enable_undo(self):
        self.undo_button.setEnabled(True)

    def disable_redo(self):
        self.redo_button.setEnabled(False)

    def enable_redo(self):
        self.redo_button.setEnabled(True)

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
        self.clear_spinners()

        self.enable_type(False)
        self.enable_domain(False)
        self.enable_length(False)

    @staticmethod
    def is_length_spinner(spinner_id: int) -> bool:
        return spinner_id == ID_SPIN_LENGTH
