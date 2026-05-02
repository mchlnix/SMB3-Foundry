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
from foundry.gui.localization import tr
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

    Attributes
    ----------
    _author_label : LinkLabel
        Clickable project-author attribution label.
    _dario_label : QLabel
        Bug-reporting contributor attribution label.
    _hukka_label : LinkLabel
        Clickable SMB3 Workshop attribution label.
    _lira_label : LinkLabel
        Clickable disassembly-parsing and autoscroll attribution label.
    _southbird_label : LinkLabel
        Clickable SMB3 disassembly attribution label.
    _spinzig_label : QLabel
        Enemy-incompatibility contributor attribution label.
    _testing_label : LinkLabel
        Clickable testing and sanity-checking attribution label.
    _thanks_label : QLabel
        Static heading for the contributor-credit section.
    _version_label : QLabel
        Label showing the translated running Foundry version string.
    _version_name : str
        Version text resolved at construction and interpolated during
        translation refresh.

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
        super(AboutDialog, self).__init__(parent, title=tr("AboutDialog", "about_smb3foundry", "About SMB3Foundry"))

        main_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self)

        image = QPixmap(str(data_dir.joinpath("foundry.ico"))).scaled(
            200, 200, mode=Qt.TransformationMode.SmoothTransformation
        )

        icon = QLabel(self)
        icon.setPixmap(image)
        icon.setContentsMargins(0, 0, 10, 0)

        main_layout.addWidget(icon)

        text_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)

        self._version_name = get_current_version_name()

        if not self._version_name.startswith("nightly"):
            self._version_name = f"v{self._version_name}"

        self._version_label = QLabel(self)
        text_layout.addWidget(self._version_label)
        text_layout.addWidget(HorizontalLine())
        self._author_label = LinkLabel(self, "")
        text_layout.addWidget(self._author_label)
        text_layout.addWidget((QLabel("", self)))
        self._thanks_label = QLabel(self)
        text_layout.addWidget(self._thanks_label)
        self._hukka_label = LinkLabel(self, "")
        text_layout.addWidget(self._hukka_label)
        self._southbird_label = LinkLabel(self, "")
        text_layout.addWidget(self._southbird_label)
        self._lira_label = LinkLabel(self, "")
        text_layout.addWidget(self._lira_label)
        self._testing_label = LinkLabel(self, "")
        text_layout.addWidget(self._testing_label)
        self._dario_label = QLabel(self)
        text_layout.addWidget(self._dario_label)
        self._spinzig_label = QLabel(self)
        text_layout.addWidget(self._spinzig_label)

        main_layout.addLayout(text_layout)

        self.setContentsMargins(10, 10, 10, 10)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh translated About dialog text without rebuilding the layout.

        Live language switching updates only Qt display text and rich-text link
        labels. The method coordinates the dialog's display state from the
        resolved Foundry build version and URL constants, so refreshes rebuild
        visible labels without changing dialog identity or opening new widgets.
        HTML anchors are part of the display boundary and their ``href`` values
        remain project-support constants rather than translated payloads.
        """
        self.setWindowTitle(tr("AboutDialog", "about_smb3foundry", "About SMB3Foundry"))
        self._version_label.setText(
            tr("AboutDialog", "smb3_foundry_version_name", "SMB3 Foundry {version_name}").format(
                version_name=self._version_name
            )
        )
        self._author_label.setText(
            tr("AboutDialog", "credit.author_michael", 'By <a href="{link}">Michael</a>').format(link=LINK_SMB3F)
        )
        self._thanks_label.setText(tr("AboutDialog", "with_thanks_to", "With thanks to:"))
        self._hukka_label.setText(
            tr(
                "AboutDialog",
                "credit.hukka_workshop",
                '<a href="{hukka_link}">Hukka</a> for <a href="{workshop_link}">SMB3 Workshop</a>',
            ).format(hukka_link=LINK_HUKKA, workshop_link=LINK_SMB3WS)
        )
        self._southbird_label.setText(
            tr(
                "AboutDialog",
                "credit.southbird_disassembly",
                '<a href="{southbird_link}">Captain Southbird</a> for the <a href="{disasm_link}">SMB3 Disassembly</a>',
            ).format(southbird_link=LINK_SOUTHBIRD, disasm_link=LINK_DISASM)
        )
        self._lira_label.setText(
            tr(
                "AboutDialog",
                "credit.lira_autoscroll",
                '<a href="{lira_link}">Lira</a> for helping to parse the disassembly and working on AutoScrolling',
            ).format(lira_link=LINK_LIRA)
        )
        self._testing_label.setText(
            tr(
                "AboutDialog",
                "credit.bluefinch_testing",
                '<a href="{bluefinch_link}">BlueFinch</a>, ZacMario and <a href="{sky_link}">SKJyannick</a> for testing and sanity checking',
            ).format(bluefinch_link=LINK_BLUEFINCH, sky_link=LINK_SKY)
        )
        self._dario_label.setText(
            tr(
                "AboutDialog",
                "credit.dario_bug_reports",
                '<a href="{dario_link}">Dario</a> for reporting many bugs and problems',
            ).format(dario_link=LINK_DARIO)
        )
        self._spinzig_label.setText(
            tr("AboutDialog", "credit.spijzig_enemy_compat", "Spinzig for compiling the enemy incompatibilities.")
        )


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
