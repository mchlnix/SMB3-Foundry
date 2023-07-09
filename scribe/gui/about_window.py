from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QBoxLayout, QLabel

from foundry import data_dir, get_current_version_name
from foundry.gui.dialogs.AboutWindow import LinkLabel
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.HorizontalLine import HorizontalLine

LINK_SMB3F = "https://github.com/mchlnix/SMB3-Foundry"
LINK_BEN = "https://www.romhacking.net/community/522/"
LINK_SMB3ME = "https://www.romhacking.net/utilities/242/"
LINK_SOUTHBIRD = "https://github.com/captainsouthbird"
LINK_DISASM = "https://github.com/captainsouthbird/smb3"


class AboutDialog(CustomDialog):
    def __init__(self, parent):
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
