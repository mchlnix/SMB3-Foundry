from foundry.gui.AboutWindow import AboutDialog


def test_open_about_window(qtbot):
    about_window = AboutDialog(None)

    about_window.show()

    qtbot.addWidget(about_window)
