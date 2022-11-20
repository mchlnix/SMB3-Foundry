import pytest
from PySide6.QtWidgets import QVBoxLayout, QWidget

from foundry.game.gfx.objects import LevelObjectFactory
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

    widget.adjustSize()
    qtbot.wait_exposed(widget)


def test_object_toolbar(qtbot):
    toolbar = ObjectToolBox(None)

    toolbar.update()
