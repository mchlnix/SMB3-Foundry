from PySide2.QtCore import Signal, SignalInstance
from PySide2.QtGui import QContextMenuEvent
from PySide2.QtWidgets import QListWidget, QWidget, QMenu

from foundry.game.level.LevelRef import LevelRef

ID_ADD_JUMP = 1
ID_DEL_JUMP = 2
ID_EDIT_JUMP = 3


class JumpList(QListWidget):
    add_jump: SignalInstance = Signal()
    edit_jump: SignalInstance = Signal()
    remove_jump: SignalInstance = Signal()

    def __init__(self, parent: QWidget, level_ref: LevelRef):
        super(JumpList, self).__init__(parent)

        self._level_ref = level_ref

        self._level_ref.data_changed.connect(self.update)
        self.itemDoubleClicked.connect(lambda _: self.edit_jump.emit())

    def update(self):
        self.clear()

        jumps = self._level_ref.jumps

        self.addItems([str(jump) for jump in jumps])

    def contextMenuEvent(self, event: QContextMenuEvent):
        item = self.itemAt(event.pos())

        menu = QMenu()

        if item is None:
            add_action = menu.addAction("Add Jump")
            add_action.triggered.connect(self.add_jump.emit)

        else:
            edit_action = menu.addAction("Edit Jump")
            edit_action.triggered.connect(self.edit_jump.emit)

            remove_action = menu.addAction("Remove Jump")
            remove_action.triggered.connect(self.remove_jump.emit)

        menu.exec_(event.globalPos())
