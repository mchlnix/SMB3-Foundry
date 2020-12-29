from foundry.core.util import FEATURE_VIDEO_LINK
from foundry.core.util.open_url import open_url
from foundry.gui.QMenus.MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater


class MenuElementFeatureVideo(AbstractMenuElementUpdater):
    """A menu element to load the feature video's link"""
    def action(self) -> None:
        """Loads the feature video"""
        open_url(FEATURE_VIDEO_LINK)

    @property
    def base_name(self) -> str:
        """The base name fro the menu element"""
        return "Feature Video on YouTube"