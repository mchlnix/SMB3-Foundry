from foundry.gui.widgets.object_toolbar.TabbedToolBox import TabbedToolBox


def test_tabbed_tool_box(qtbot):
    ttb = TabbedToolBox(None)

    qtbot.addWidget(ttb)
