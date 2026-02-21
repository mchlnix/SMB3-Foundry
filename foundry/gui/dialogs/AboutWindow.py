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
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent, title=_("About SMB3Foundry"))

        main_layout = QBoxLayout(QBoxLayout.LeftToRight, self)

        image = QPixmap(str(data_dir.joinpath("foundry.ico"))).scaled(
            200, 200, mode=Qt.SmoothTransformation
        )

        icon = QLabel(self)
        icon.setPixmap(image)

        main_layout.addWidget(icon)

        text_layout = QBoxLayout(QBoxLayout.TopToBottom)

        text_layout.addWidget(
            QLabel(f"SMB3 Foundry v{get_current_version_name()}", self)
        )
        text_layout.addWidget(HorizontalLine())
        text_layout.addWidget(
            LinkLabel(self, _('By <a href="%s">Michael</a>') % LINK_SMB3F)
        )
        text_layout.addWidget((QLabel("", self)))
        text_layout.addWidget(QLabel(_("With thanks to:"), self))
        text_layout.addWidget(
            LinkLabel(
                self,
                _(
                    '<a href="%(hukka)s">Hukka</a> for <a href="%(smb3ws)s">SMB3 Workshop</a>'
                )
                % {"hukka": LINK_HUKKA, "smb3ws": LINK_SMB3WS},
            )
        )
        text_layout.addWidget(
            LinkLabel(
                self,
                _(
                    '<a href="%(southbird)s">Captain Southbird</a> '
                    'for the <a href="%(disasm)s">SMB3 Disassembly</a>'
                )
                % {"southbird": LINK_SOUTHBIRD, "disasm": LINK_DISASM},
            )
        )
        text_layout.addWidget(
            LinkLabel(
                self,
                _(
                    '<a href="%s">Lira</a> for helping to parse the disassembly and working on AutoScrolling'
                )
                % LINK_LIRA,
            )
        )
        text_layout.addWidget(
            LinkLabel(
                self,
                _(
                    '<a href="%(bluefinch)s">BlueFinch</a>, ZacMario and '
                    '<a href="%(sky)s">SKJyannick</a> for testing and sanity checking'
                )
                % {"bluefinch": LINK_BLUEFINCH, "sky": LINK_SKY},
            )
        )
        text_layout.addWidget(
            QLabel(
                _('<a href="%s">Dario</a> for reporting many bugs and problems')
                % LINK_DARIO,
                self,
            )
        )
        text_layout.addWidget(
            QLabel(_("Spinzig for compiling the enemy incompatibilities."), self)
        )

        main_layout.addLayout(text_layout)

        self.setContentsMargins(10, 10, 10, 10)


class LinkLabel(QLabel):
    def __init__(self, parent, text):
        super(LinkLabel, self).__init__(parent)

        self.setText(text)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)
