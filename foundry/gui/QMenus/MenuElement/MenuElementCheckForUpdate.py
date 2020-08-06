from typing import Tuple, Optional

from PySide2.QtGui import Qt
from PySide2.QtWidgets import QMessageBox

from foundry.core.util.ask_for_update import ask_for_update
from foundry.core.util.get_current_version_name import get_current_version_name
from foundry.core.util.get_latest_version_name import get_latest_version_name
from foundry.gui.QMenus.MenuElement.AbstractMenuElementUpdater import AbstractMenuElementUpdater


class MenuElementCheckForUpdate(AbstractMenuElementUpdater):
    """Menu Element that checks for an update"""
    def __init__(self, parent, add_action: bool = True) -> None:
        super().__init__(parent, add_action)
        self.action.attach_observer(ask_for_update)
        self.action.attach_observer(self.confirm_up_to_date)
        self.action.attach_observer(lambda *_: self.parent.setCursor(Qt.ArrowCursor))

    def action(self) -> Tuple[Optional[bool], Optional[str], Optional[str]]:
        """The main method for the Menu Element"""
        self.parent.setCursor(Qt.WaitCursor)

        current_version = get_current_version_name()

        try:
            latest_version = get_latest_version_name()
        except ValueError as ve:
            QMessageBox.critical(self.parent, "Error while checking for updates", f"Error: {ve}")
            return None, current_version, None

        return current_version != latest_version, current_version, latest_version

    def confirm_up_to_date(self, needs_updating: bool, current_version: str, _: str):
        """Confirms we are up to data"""
        if needs_updating is None:
            return
        elif not needs_updating:
            QMessageBox.information(self.parent, "No newer release", f"Version {current_version} is up to date.")

    @property
    def base_name(self) -> str:
        """The base name for menu element"""
        return "Check For Updates"