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
from foundry.gui.localization import tr
from foundry.gui.widgets.HorizontalLine import HorizontalLine

LINK_SMB3F = "https://github.com/mchlnix/SMB3-Foundry"
LINK_BEN = "https://www.romhacking.net/community/522/"
LINK_SMB3ME = "https://www.romhacking.net/utilities/242/"
LINK_SOUTHBIRD = "https://github.com/captainsouthbird"
LINK_DISASM = "https://github.com/captainsouthbird/smb3"
TR_CONTEXT = "ScribeAboutDialog"


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

    Attributes
    ----------
    version_label : QLabel
        Displays the catalog-backed version line built from the running
        application version.
    author_label : LinkLabel
        Rich-text attribution link for the Scribe/Foundry project author.
    thanks_label : QLabel
        Static catalog-backed intro label for the acknowledgement links.
    editor_label : LinkLabel
        Rich-text reference to the predecessor SMB3 map editor.
    disassembly_label : LinkLabel
        Rich-text reference to the SMB3 disassembly used as project context.

    Notes
    -----
    The labels are owned by this dialog and refreshed only through
    :meth:`retranslate_ui`. Their link URLs are stable project references, not
    editable settings or persisted data.

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
        credit and reference labels. This is a display-state boundary: no later
        method commits ROM, settings, or undo data, so the constructor is where
        Scribe's about-screen provenance becomes concrete Qt widgets that
        :meth:`retranslate_ui` can refresh in place.

        Parameters
        ----------
        parent : object
            Parent Qt widget that owns this dialog.
        """
        super(AboutDialog, self).__init__(parent, title=tr(TR_CONTEXT, "about_smb3_scribe", "About SMB3 Scribe"))

        main_layout = QBoxLayout(QBoxLayout.LeftToRight, self)

        image = QPixmap(str(data_dir.joinpath("scribe_feather.png"))).scaled(200, 200, mode=Qt.SmoothTransformation)

        icon = QLabel(self)
        icon.setPixmap(image)

        main_layout.addWidget(icon)

        main_layout.addSpacing(25)

        text_layout = QBoxLayout(QBoxLayout.TopToBottom)

        text_layout.addStretch(1)
        self.version_label = QLabel(self)
        text_layout.addWidget(self.version_label)
        text_layout.addWidget(HorizontalLine())
        self.author_label = LinkLabel(self, "")
        text_layout.addWidget(self.author_label)
        self.thanks_label = QLabel(self)
        text_layout.addWidget(self.thanks_label)
        self.editor_label = LinkLabel(self, "")
        text_layout.addWidget(self.editor_label)
        self.disassembly_label = LinkLabel(self, "")
        text_layout.addWidget(self.disassembly_label)
        text_layout.addStretch(1)

        main_layout.addLayout(text_layout)

        self.setContentsMargins(10, 10, 10, 10)
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh dialog text after the active translator changes.

        The method is the dialog's live-language boundary. It rewrites only
        visible labels and the window title from catalog entries while
        preserving the stable URLs and version source used to format those
        labels. No state from the about dialog feeds undo history, settings, or
        ROM data, so retranslation is a pure display refresh.
        """
        self.setWindowTitle(tr(TR_CONTEXT, "about_smb3_scribe", "About SMB3 Scribe"))
        self.version_label.setText(
            tr(TR_CONTEXT, "smb3_scribe_v_version", "SMB3 Scribe v{version}").format(version=get_current_version_name())
        )
        self.author_label.setText(
            tr(TR_CONTEXT, "credit.author_michael", 'By <a href="{link}">Michael</a>').format(link=LINK_SMB3F)
        )
        self.thanks_label.setText(tr(TR_CONTEXT, "with_thanks_to", "With thanks to:"))
        self.editor_label.setText(
            tr(
                TR_CONTEXT,
                "credit.beneficii_map_editor",
                '<a href="{ben_link}">Beneficii</a> for their <a href="{editor_link}">SMB3 Map Editor</a>',
            ).format(
                ben_link=LINK_BEN,
                editor_link=LINK_SMB3ME,
            )
        )
        self.disassembly_label.setText(
            tr(
                TR_CONTEXT,
                "credit.southbird_disassembly",
                '<a href="{southbird_link}">Captain Southbird</a> for the <a href="{disasm_link}">SMB3 Disassembly</a>',
            ).format(
                southbird_link=LINK_SOUTHBIRD,
                disasm_link=LINK_DISASM,
            )
        )
