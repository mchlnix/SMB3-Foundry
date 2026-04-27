"""Show SMB3 Scribe's version, credits, and project-reference links.

This module owns Scribe's small About dialog. The dialog does not participate
in editing workflows; instead, it collects the running build version, the
application feather icon, and the external links that explain Scribe's lineage
and supporting SMB3 references in one place. Maintainers usually touch this
module when Scribe's branding, attribution text, or project references change.

See Also
--------
foundry.gui.dialogs.CustomDialog
    Base dialog class that supplies Foundry's standard close behavior.
foundry.gui.dialogs.AboutWindow.LinkLabel
    Rich-text label helper reused here for clickable attribution rows.
"""

from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QBoxLayout, QLabel

from foundry import data_dir, get_current_version_name
from foundry.gui.dialogs.AboutWindow import LinkLabel
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.widgets.HorizontalLine import HorizontalLine

LINK_SMB3F = "https://github.com/mchlnix/SMB3-Foundry"
LINK_BEN = "https://www.romhacking.net/community/522/"
LINK_SMB3ME = "https://www.romhacking.net/utilities/242/"
LINK_SOUTHBIRD = "https://github.com/captainsouthbird"
LINK_DISASM = "https://github.com/captainsouthbird/smb3"


class AboutDialog(CustomDialog):
    """Display Scribe's About dialog contents.

    The dialog is a static support surface for the Scribe GUI. It presents the
    running version string together with a short set of acknowledgements and
    external links so users can trace the tool back to the upstream project,
    predecessor editor work, and the SMB3 disassembly that informs the wider
    codebase. The class is intentionally small, but it defines the whole
    content layout for that workflow.

    Parameters
    ----------
    parent : object
        Parent Qt widget that owns this dialog.

    See Also
    --------
    foundry.gui.dialogs.AboutWindow.LinkLabel
        Label helper used for clickable attribution rows.
    """

    def __init__(self, parent):
        """Build the icon-and-credits layout for the About dialog.

        Construction is the full dialog workflow for this class. It loads the
        bundled ``scribe_feather.png`` asset from ``data_dir`` into the left
        column, resolves the running version string with
        ``get_current_version_name()``, and then assembles the right column of
        credit and reference labels. No later method mutates this content, so
        the constructor is also the point where Scribe's about-screen
        provenance data becomes concrete Qt widgets.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this dialog.
        """
        super(AboutDialog, self).__init__(parent, title="About SMB3 Scribe")

        main_layout = QBoxLayout(QBoxLayout.LeftToRight, self)

        image = QPixmap(str(data_dir.joinpath("scribe_feather.png"))).scaled(200, 200, mode=Qt.SmoothTransformation)

        icon = QLabel(self)
        icon.setPixmap(image)

        main_layout.addWidget(icon)

        main_layout.addSpacing(25)

        text_layout = QBoxLayout(QBoxLayout.TopToBottom)

        text_layout.addStretch(1)
        text_layout.addWidget(QLabel(f"SMB3 Scribe v{get_current_version_name()}", self))
        text_layout.addWidget(HorizontalLine())
        text_layout.addWidget(LinkLabel(self, f'By <a href="{LINK_SMB3F}">Michael</a>'))
        text_layout.addWidget(QLabel("With thanks to:", self))
        text_layout.addWidget(
            LinkLabel(
                self,
                f'<a href="{LINK_BEN}">Beneficii</a> for their <a href="{LINK_SMB3ME}">SMB3 Map Editor</a>',
            )
        )
        text_layout.addWidget(
            LinkLabel(
                self,
                f'<a href="{LINK_SOUTHBIRD}">Captain Southbird</a> '
                f'for the <a href="{LINK_DISASM}">SMB3 Disassembly</a>',
            )
        )
        text_layout.addStretch(1)

        main_layout.addLayout(text_layout)

        self.setContentsMargins(10, 10, 10, 10)
