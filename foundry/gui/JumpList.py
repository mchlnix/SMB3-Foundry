from PySide6.QtCore import Signal, SignalInstance
from PySide6.QtGui import QContextMenuEvent
from PySide6.QtWidgets import QListWidget, QMenu, QWidget

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

        self.setWhatsThis(
            "<b>Jump List</b><br/>"
            "Every level can designate another level to jump to, in case a pipe or a door is entered. This is done in "
            "the header, which can be edited with the Header Editor. While only one such level can be defined, where "
            "and how to enter that level can be defined multiple times with multiple jumps.<br/>"
            "A jump is valid for one screen, a 16-block wide/high section of the level, depending on if the level is "
            "vertical or not, and all objects within that section, capable of handling a jump, will jump to the same "
            "position in the same way. To see where these jump zones are, enable the Jump Zone option in the View menu."
            "<br/><br/>"
            "Tip: By having multiple jumps with different entry positions, you could make it look, like you are "
            "jumping to two different levels, when, in fact, you are jumping to two different sections of the same "
            "level."
        )

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

        menu.exec(event.globalPos())
