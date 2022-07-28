from foundry.gui.menus.help_menu import HelpMenu as FoundryHelpMenu
from scribe.gui.about_window import AboutDialog


class HelpMenu(FoundryHelpMenu):
    def __init__(self, parent):
        super(HelpMenu, self).__init__(parent)

        self.removeAction(self._enemy_compat_action)

    def on_about(self):
        about = AboutDialog(self._parent)

        about.show()
