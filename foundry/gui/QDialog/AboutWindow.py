from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QBoxLayout, QLabel

from foundry import data_dir, get_current_version_name
from foundry.core.util import LINK_MICHAEL, LINK_JOE_SMO, LINK_PIJOKRA, LINK_BLUEFINCH, LINK_SKYYANNICK, LINK_HUKKA, \
    LINK_SMB3WORKSHOP, LINK_SOUTHBIRD, LINK_DISASM
from foundry.gui.AboutWindow import QHLine
from foundry.gui.QDialog import Dialog
from foundry.gui.QLabel.LinkLabel import LinkLabel


class AboutDialog(Dialog):
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
                                              f'  • <a href="{LINK_SKYYANNICK}">SKJyannick</a>'))
        text_layout.addWidget(LinkLabel(self, f''))
        text_layout.addWidget(LinkLabel(self, f'Special Thanks To:'))
        text_layout.addWidget(LinkLabel(self, f'  • <a href="{LINK_HUKKA}">Hukka</a> for our predecessor '
                                              f'<a href="{LINK_SMB3WORKSHOP}">SMB3 Workshop</a>'))
        text_layout.addWidget(LinkLabel(self, f'  • <a href="{LINK_SOUTHBIRD}">Captain Southbird</a> '
                                              f'for the tremendous work on the '
                                              f'<a href="{LINK_DISASM}">SMB3 Disassembly</a>'))
        text_layout.addWidget(LinkLabel(self, f'  • And most importantly you!'))

        main_layout.addLayout(text_layout)