"""Adapt Foundry's help menu to Scribe's smaller support surface.

This module reuses the shared Foundry help menu implementation for Scribe, then
removes the enemy-compatibility link that only makes sense in the level editor.
The remaining menu keeps the same outward-facing support workflow: the main
window owns the menu, inherited actions route through the shared trigger
dispatcher, and the local about action opens Scribe's dialog.

See Also
--------
foundry.gui.menus.help_menu.HelpMenu
    Supplies the shared help-menu structure and action-dispatch workflow.
scribe.gui.about_window
    Provides the Scribe-specific about dialog opened from this menu.
"""

from foundry.gui.menus.help_menu import HelpMenu as FoundryHelpMenu
from scribe.gui.about_window import AboutDialog


class HelpMenu(FoundryHelpMenu):
    """Expose the shared help workflow with Scribe-specific pruning.

    Scribe reuses Foundry's help menu so update checks, reference links, and
    the about entry behave the same way across both applications. This subclass
    narrows that surface to Scribe's world-map tooling by removing the enemy
    compatibility link while preserving the inherited action-dispatch and menu
    layout behavior.

    Parameters
    ----------
    parent : QMainWindow
        Main window that owns the menu bar, receives inherited update-check
        requests, and becomes the parent for the Scribe about dialog.
    """

    def __init__(self, parent):
        """Create Scribe's help menu from the shared Foundry menu layout.

        Construction first delegates to :class:`foundry.gui.menus.help_menu.HelpMenu`
        so Scribe inherits the shared help actions, trigger routing, and menu
        ordering used by the editor shell. It then removes the enemy
        compatibility entry because Scribe edits world-map metadata rather than
        level objects, so that SMB3-specific compatibility reference would send
        maintainers toward the wrong workflow. The resulting menu keeps the
        shared support boundary intact while tailoring the visible actions to
        Scribe's toolset.

        Parameters
        ----------
        parent : QMainWindow
            Main window that owns the menu and later parents the about dialog.
        """
        super(HelpMenu, self).__init__(parent)

        self.removeAction(self._enemy_compat_action)

    def on_about(self):
        """Show Scribe's about dialog from the inherited help workflow.

        The shared help menu dispatches its about action here after the user
        selects the menu entry. This override preserves the inherited trigger
        path while swapping in Scribe's dialog implementation so the window
        identity, versioning, and project framing stay specific to the world
        editor.
        """
        about = AboutDialog(self._parent)

        about.show()
