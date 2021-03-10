from foundry.gui.PaletteViewer import ColorTable


def test_open_color_palette(qtbot):
    color_palette = ColorTable()

    color_palette.ok_clicked.connect(print)

    qtbot.addWidget(color_palette)
