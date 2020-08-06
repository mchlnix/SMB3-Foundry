from PySide2.QtWidgets import QPushButton, QMessageBox

from foundry.core.util import RELEASES_LINK
from foundry.core.util.icon import icon
from foundry.core.util.open_url import open_url


def ask_for_update(needs_updating: bool, _: str, latest_version: str) -> None:
    """Asks the player for an update if needed"""
    if needs_updating is None:
        return
    elif needs_updating:
        latest_release_url = f"{RELEASES_LINK}/tag/{latest_version}"

        go_to_github_button = QPushButton(icon("external-link.svg"), "Go to latest release")
        go_to_github_button.clicked.connect(lambda *_: open_url(latest_release_url))

        info_box = QMessageBox(
            QMessageBox.Information, "New release available", f"New Version {latest_version} is available."
        )

        info_box.addButton(QMessageBox.Cancel)
        info_box.addButton(go_to_github_button, QMessageBox.AcceptRole)

        info_box.exec_()