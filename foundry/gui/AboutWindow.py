from PySide2.QtGui import QPixmap, Qt
from PySide2.QtWidgets import QBoxLayout, QFrame, QLabel

from foundry import data_dir, get_current_version_name
from foundry.gui.CustomDialog import CustomDialog

LINK_SMB3_FOUNDRY = "https://github.com/mchlnix/SMB3-Foundry"
LINK_SMB3_PRIME = "https://smb3p.kafuka.org/index.php"
LINK_SMB3_WIKI = "https://www.smb3prime.org/wiki/Main_Page"
LINK_HUKKA = "http://hukka.ncn.fi/index.php?about"
LINK_SMB3WORKSHOP = "https://www.romhacking.net/utilities/298/"
LINK_SOUTHBIRD = "https://github.com/captainsouthbird"
LINK_DISASM = "https://github.com/captainsouthbird/smb3"
LINK_BLUEFINCH = "https://www.twitch.tv/bluefinch3000"
LINK_JOE_SMO = "https://github.com/TheJoeSmo"
LINK_PIJOKRA = "https://github.com/PiJoKra"
LINK_MICHAEL = "https://github.com/mchlnix"


class AboutDialog(CustomDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent, title="About SMB3Foundry")

        main_layout = QBoxLayout(QBoxLayout.LeftToRight, self)

        image = QPixmap(str(data_dir.joinpath("foundry.ico"))).scaled(200, 200)

        icon = QLabel(self)
        icon.setPixmap(image)

        main_layout.addWidget(icon)

        text_layout = QBoxLayout(QBoxLayout.TopToBottom)

        text_layout.addWidget(QLabel(f"SMB3 Foundry v{get_current_version_name()}", self))
        text_layout.addWidget(QHLine())
        text_layout.addWidget(LinkLabel(self, f'Authors:'))
        text_layout.addWidget(LinkLabel(self, f'  • <a href="{LINK_MICHAEL}">Michael</a>      '
                                              f'  • <a href="{LINK_JOE_SMO}">Joe Smo</a>      '
                                              f'  • <a href="{LINK_PIJOKRA}">PiJoKra</a>'))
        text_layout.addWidget(LinkLabel(self, f''))
        text_layout.addWidget(LinkLabel(self, f'Testers: '))
        text_layout.addWidget(LinkLabel(self, f'  • <a href="{LINK_BLUEFINCH}">BlueFinch</a>  '
                                              f'  • ZacMario  '
                                              f'  • SKJyannick'))
        text_layout.addWidget(LinkLabel(self, f''))
        text_layout.addWidget(LinkLabel(self, f'Special Thanks To:'))
        text_layout.addWidget(LinkLabel(self, f'  • <a href="{LINK_HUKKA}">Hukka</a> for our predecessor '
                                              f'<a href="{LINK_SMB3WORKSHOP}">SMB3 Workshop</a>'))
        text_layout.addWidget(LinkLabel(self, f'  • <a href="{LINK_SOUTHBIRD}">Captain Southbird</a> '
                                              f'for the tremendous work on the '
                                              f'<a href="{LINK_DISASM}">SMB3 Disassembly</a>'))
        text_layout.addWidget(LinkLabel(self, f'  • And most importantly you!'))

        main_layout.addLayout(text_layout)


class LinkLabel(QLabel):
    def __init__(self, parent, text):
        super(LinkLabel, self).__init__(parent)

        self.setText(text)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)


# taken from https://stackoverflow.com/a/41068447/4252230
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
