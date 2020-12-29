from foundry.gui.QDialog.AboutWindow import AboutDialog


def test_open_about_window(qtbot):
    about_window = AboutDialog(None)

    qtbot.addWidget(about_window)
