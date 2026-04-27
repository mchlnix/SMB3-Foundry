"""Show Foundry's version, lineage, and project-support links.

This module owns the non-editing dialog that surfaces the running build
version, project attribution, and the external references that explain where
Foundry came from. It sits on the support side of the GUI rather than the
editing workflow, but it still matters for maintainers because it is the one
place the application ties the shipped build back to upstream code,
disassembly work, and community contributors.

See Also
--------
foundry.gui.dialogs.CustomDialog
    Base dialog class that supplies Foundry's standard close behavior.
"""

from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QBoxLayout, QLabel

from foundry import data_dir, get_current_version_name
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.widgets.HorizontalLine import HorizontalLine

LINK_SMB3F = "https://github.com/mchlnix/SMB3-Foundry"
LINK_HUKKA = "http://hukka.ncn.fi/index.php?about"
LINK_SMB3WS = "https://www.romhacking.net/utilities/298/"
LINK_SOUTHBIRD = "https://github.com/captainsouthbird"
LINK_DISASM = "https://github.com/captainsouthbird/smb3"
LINK_BLUEFINCH = "https://www.twitch.tv/bluefinch3000"
LINK_SKY = "https://www.youtube.com/channel/UCnI_HjFGbyRmfOBWzzxK6LA"
LINK_LIRA = "https://github.com/LiraOnGithub"
LINK_DARIO = "https://github.com/Dariosky-01"


class AboutDialog(CustomDialog):
    """Show version, credits, and project links for Foundry.

    The dialog is informational rather than editable: it displays the running
    build version, project attribution, and a set of external links to the
    Foundry project and related SMB3 tooling. It also serves as a lightweight
    provenance screen for the editor by tying the running build back to the
    upstream project, predecessor tools, disassembly work, and community
    contributors that inform how Foundry understands SMB3. That gives the
    application a maintained place to surface lineage and support links without
    mixing those concerns into the editing workflows themselves.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.

    See Also
    --------
    LinkLabel
        Rich-text label helper used for clickable attribution links.
    """

    def __init__(self, parent):
        """Build the static About dialog layout.

        The constructor assembles the dialog in three stages: it creates the
        icon panel, resolves the running version string, and then builds the
        stacked attribution links that connect the running build to upstream
        project pages and SMB3 reverse-engineering references. That setup is
        the one-time UI workflow that turns version state and support links
        into the finished dialog content.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        """
        super(AboutDialog, self).__init__(parent, title="About SMB3Foundry")

        main_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self)

        image = QPixmap(str(data_dir.joinpath("foundry.ico"))).scaled(
            200, 200, mode=Qt.TransformationMode.SmoothTransformation
        )

        icon = QLabel(self)
        icon.setPixmap(image)
        icon.setContentsMargins(0, 0, 10, 0)

        main_layout.addWidget(icon)

        text_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)

        version_name = get_current_version_name()

        if not version_name.startswith("nightly"):
            version_name = f"v{version_name}"

        text_layout.addWidget(QLabel(f"SMB3 Foundry {version_name}", self))
        text_layout.addWidget(HorizontalLine())
        text_layout.addWidget(LinkLabel(self, f'By <a href="{LINK_SMB3F}">Michael</a>'))
        text_layout.addWidget((QLabel("", self)))
        text_layout.addWidget(QLabel("With thanks to:", self))
        text_layout.addWidget(
            LinkLabel(
                self,
                f'<a href="{LINK_HUKKA}">Hukka</a> for <a href="{LINK_SMB3WS}">SMB3 Workshop</a>',
            )
        )
        text_layout.addWidget(
            LinkLabel(
                self,
                f'<a href="{LINK_SOUTHBIRD}">Captain Southbird</a> '
                f'for the <a href="{LINK_DISASM}">SMB3 Disassembly</a>',
            )
        )
        text_layout.addWidget(
            LinkLabel(
                self,
                f'<a href="{LINK_LIRA}">Lira</a> for helping to parse the disassembly and working on AutoScrolling',
            )
        )
        text_layout.addWidget(
            LinkLabel(
                self,
                f'<a href="{LINK_BLUEFINCH}">BlueFinch</a>, ZacMario and '
                f'<a href="{LINK_SKY}">SKJyannick</a> for testing and sanity checking',
            )
        )
        text_layout.addWidget(QLabel(f'<a href="{LINK_DARIO}">Dario</a> for reporting many bugs and problems', self))
        text_layout.addWidget(QLabel("Spinzig for compiling the enemy incompatibilities.", self))

        main_layout.addLayout(text_layout)

        self.setContentsMargins(10, 10, 10, 10)


class LinkLabel(QLabel):
    """Render a clickable rich-text label inside the About dialog.

    The helper keeps link configuration out of the dialog layout code so each
    attribution row can be created as a normal label widget that already knows
    how to open external URLs. That keeps the About dialog declarative and lets
    credits behave like ordinary Qt labels while still participating in the
    project's documentation-and-support surface. It is a tiny widget, but it
    captures one repeated policy for the whole dialog: rich text should behave
    like an external reference, not like editable content.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    text : str
        Rich-text label contents.

    See Also
    --------
    AboutDialog
        Uses these labels for project and attribution links.

    Notes
    -----
    This helper keeps the About dialog's layout code focused on attribution
    content rather than on repeatedly configuring link behavior for each row.
    """

    def __init__(self, parent, text):
        """Create a rich-text label that opens external links.

        The helper turns one attribution string into a ready-to-use external
        reference widget, which keeps the About dialog layout code focused on
        support content instead of repeatedly configuring Qt link behavior. It
        is the small widget-construction boundary that turns support text into
        the clickable label state reused across the whole dialog.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        text : str
            Rich-text label contents.
        """
        super(LinkLabel, self).__init__(parent)

        self.setText(text)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.setOpenExternalLinks(True)
