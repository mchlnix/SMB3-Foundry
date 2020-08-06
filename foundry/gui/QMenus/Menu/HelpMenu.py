from foundry.gui.QMenus.HelpMenu import AboutMenuElement
from foundry.gui.QMenus.MenuElement.MenuElementDiscord import MenuElementDiscord
from foundry.gui.QMenus.MenuElement.MenuElementGithub import MenuElementGithub
from foundry.gui.QMenus.MenuElement.MenuElementFeatureVideo import MenuElementFeatureVideo
from foundry.gui.QMenus.MenuElement.MenuElementCheckForUpdate import MenuElementCheckForUpdate
from foundry.gui.QMenus.Menu.Menu import Menu


class HelpMenu(Menu):
    """A menu for providing help"""
    def __init__(self, parent):
        super().__init__(parent, "Help")
        self.parent = parent

        self.updater_action = MenuElementCheckForUpdate(self.parent, False)
        self.add_action(self.updater_action.name, self.updater_action.action)
        self.addSeparator()
        self.feature_video_action = MenuElementFeatureVideo(self)
        self.git_action = MenuElementGithub(self)
        self.discord_action = MenuElementDiscord(self)
        self.about_action = AboutMenuElement(self.parent, False)
        self.addSeparator()
        self.add_action(self.about_action.name, self.about_action.action)