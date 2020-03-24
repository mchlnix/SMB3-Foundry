import pytest
from PySide2.QtWidgets import QWidget, QVBoxLayout

from foundry.game.gfx.objects.LevelObjectFactory import LevelObjectFactory
from foundry.gui.ObjectToolBox import ObjectIcon, ObjectToolBox
from smb3parse.objects.object_set import PLAINS_GRAPHICS_SET, PLAINS_OBJECT_SET


@pytest.mark.parametrize("domain, obj_index", [(0, 0xA0), (0, 0xA8)])
def test_object_icon(domain, obj_index, qtbot):
    factory = LevelObjectFactory(PLAINS_OBJECT_SET, PLAINS_GRAPHICS_SET, 0, [], False, True)

    level_object = factory.from_properties(domain, obj_index, 0, 0, None, 0)

    widget = QWidget()
    widget.setLayout(QVBoxLayout())

    widget.layout().addStretch()
    widget.layout().addWidget(ObjectIcon(level_object))
    widget.layout().addStretch()

    widget.show()
    widget.adjustSize()
    qtbot.wait_for_window_shown(widget)


def test_object_toolbar(qtbot):
    toolbar = ObjectToolBox(None)

    toolbar.update()

    toolbar.show()
    qtbot.wait_for_window_shown(toolbar)
