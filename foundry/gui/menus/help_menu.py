"""Host help, reference, and community-entry actions for the main window.

This module owns the top-level Help menu used by the Foundry editor shell. It
collects update checks, Qt context-help mode, project/community links, and the
about dialog into one outward-facing support surface for the main window.

See Also
--------
foundry.gui.FoundryMainWindow
    Owns the menu bar and the update workflow invoked from this menu.
foundry.gui.dialogs.AboutWindow
    Supplies the about dialog opened by the menu.
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWhatsThis

from foundry import (
    discord_link,
    enemy_compat_link,
    feature_video_link,
    github_link,
    icon,
    open_url,
)
from foundry.gui.dialogs.AboutWindow import AboutDialog
from foundry.gui.MainWindow import MainWindow


class HelpMenu(QMenu):
    """Expose help, documentation, and community-entry actions.

    The help menu collects the editor's outward-facing support paths: update
    checks, Qt's ``What's This?`` inspection mode, external reference links,
    and the about dialog. Keeping those actions in one menu lets the main
    window surface both in-app help and SMB3/Foundry community resources from a
    single place.

    Parameters
    ----------
    parent : MainWindow
        Main window that owns the menu and implements the update-check
        workflow.
    title : str, optional
        Menu title shown in the main window.

    Attributes
    ----------
    _parent : MainWindow
        Main window that owns the menu actions.
    check_updates_action : QAction
        Action that runs the manual update check.
    whats_this_action : QAction
        Action that enters Qt's context-help mode.
    _video_action : QAction
        Action that opens the feature video.
    _repo_action : QAction
        Action that opens the project repository.
    _discord_action : QAction
        Action that opens the SMB3 ROM hacking Discord.
    _enemy_compat_action : QAction
        Action that opens the enemy compatibility reference.
    _about_action : QAction
        Action that opens the about dialog.
    """

    def __init__(self, parent: MainWindow, title="&Help"):
        """Create the help menu for the main editor window.

        Construction sets up the full help-routing surface that the main window
        exposes from its menu bar. The first stage stores the owning window and
        connects the menu-wide ``triggered`` signal to ``_on_trigger`` so every
        later action uses one dispatcher. The second stage adds the in-editor
        support entries for manual update checks and Qt's ``What's This?``
        inspection mode. The third stage groups the outbound project and
        community links that leave the editor and open Foundry or SMB3
        resources in the browser. The final stage adds the about entry, which
        stays in-process and opens the editor's identity dialog. That staged
        construction matters because the menu is more than a list of labels: it
        establishes the complete boundary between the main window's passive help
        affordance and the concrete support path that is launched when a user
        picks an action.

        Parameters
        ----------
        parent : MainWindow
            Main window that owns the menu and implements the update-check
            workflow.
        title : str, optional
            Menu title shown in the main window.
        """
        super(HelpMenu, self).__init__(title)

        self._parent = parent

        self.triggered.connect(self._on_trigger)

        self.check_updates_action = self.addAction("Check for Updates")
        self.check_updates_action.setIcon(icon("bell.svg"))

        self.whats_this_action = QWhatsThis.createAction()
        self.whats_this_action.setWhatsThis("Click on parts of the editor, to receive help information.")
        self.whats_this_action.setIcon(icon("help-circle.svg"))
        self.whats_this_action.setText("Starts 'What's this?' mode")
        self.addAction(self.whats_this_action)

        self.addSeparator()

        self._video_action = self.addAction("Feature Video on YouTube")
        self._video_action.setIcon(icon("youtube.svg"))

        self._repo_action = self.addAction("Github Repository")
        self._repo_action.setIcon(icon("github.svg"))

        self._discord_action = self.addAction("SMB3 Rom Hacking Discord")
        self._discord_action.setIcon(icon("message-square.svg"))

        self.addSeparator()

        self._enemy_compat_action = self.addAction("Enemy Compatibility")
        self._enemy_compat_action.setIcon(icon("compass.svg"))

        self.addSeparator()

        self._about_action = self.addAction("About")
        self._about_action.setIcon(icon("info.svg"))

    def _on_trigger(self, action: QAction):
        """Dispatch help-menu actions to the matching resource or dialog.

        Parameters
        ----------
        action : QAction
            Triggered action from this menu.
        """
        if action is self.check_updates_action:
            self._parent.check_for_update(honor_ignore=False, in_background=False)

        elif action is self._video_action:
            open_url(feature_video_link)

        elif action is self._repo_action:
            open_url(github_link)

        elif action is self._discord_action:
            open_url(discord_link)

        elif action is self._enemy_compat_action:
            open_url(enemy_compat_link)

        elif action is self._about_action:
            self.on_about()

    def on_about(self):
        """Show the about dialog for the editor."""
        about = AboutDialog(self._parent)

        about.show()
