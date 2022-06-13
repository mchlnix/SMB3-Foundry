from foundry.gui.TabbedToolBox import TabbedToolBox


def test_tabbed_tool_box(qtbot):
    ttb = TabbedToolBox(None)

    qtbot.addWidget(ttb)

    ttb.show()
