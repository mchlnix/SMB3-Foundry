from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
    QVBoxLayout,
)

from foundry import FNS_FILE_FILTER, SMB3_ASM_FILE_FILTER
from foundry.gui.dialogs.CustomDialog import CustomDialog


class FnsAsmLoadDialog(CustomDialog):
    def __init__(self, parent, cur_fns_file: str = "", current_asm_file: str = ""):
        super().__init__(parent, title="Update Globals from files")

        self.fns_path = cur_fns_file
        self._fns_is_good = False

        self.asm_path = current_asm_file
        self._asm_is_good = False

        vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()

        explanation = QLabel("Provide an FNS file and the smb3.asm file from your project.")
        explanation.setWordWrap(True)
        explanation.setMargin(5)

        question_label = QLabel()
        question_label.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxInformation))
        question_label.setToolTip(
            "A FNS file is a by-product of compiling a Rom file from assembly code.\n"
            "It has all the labels used in the code and their positions as they would be in the NES's memory.\n"
            "Some of these labels are used by the editor to find important data, like levels, palette colors, etc.\n"
            "The editor, however, needs to know where the code these labels describe, is in the Rom file.\n"
            "By default the editor ships with these addresses for the unaltered US SMB3 Rom, but if you have\n"
            "made changes to the code, and things moved around, those addresses might not be valid anymore.\n"
            "For that purpose, the editor needs the FNS file and your smb3.asm file as well, to generate the location\n"
            "in the Rom for every label in the FNS file."
        )

        hbox.addWidget(explanation)
        hbox.addWidget(question_label)

        vbox.addLayout(hbox)

        self._fns_line_edit = QLineEdit()
        self._fns_line_edit.textChanged.connect(self._check_fns_file)

        self._fns_line_edit.setPlaceholderText("Path to FNS file.")

        self._fns_check_icon = QLabel()
        self._fns_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxCritical))

        self._fns_open_button = QPushButton()
        self._fns_open_button.pressed.connect(self._get_fns_file)
        self._fns_open_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))

        hbox = QHBoxLayout()
        hbox.addWidget(self._fns_line_edit, stretch=2)
        hbox.addWidget(self._fns_check_icon)
        hbox.addWidget(self._fns_open_button)
        vbox.addLayout(hbox)

        self._asm_line_edit = QLineEdit()
        self._asm_line_edit.textChanged.connect(self._check_asm_file)

        self._asm_line_edit.setPlaceholderText("Path to smb3.asm file.")

        self._asm_check_icon = QLabel()
        self._asm_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxCritical))

        self._asm_open_button = QPushButton()
        self._asm_open_button.pressed.connect(self._get_asm_file)
        self._asm_open_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))

        hbox = QHBoxLayout()
        hbox.addWidget(self._asm_line_edit, stretch=2)
        hbox.addWidget(self._asm_check_icon)
        hbox.addWidget(self._asm_open_button)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.pressed.connect(self.reject)

        self._ok_button = QPushButton("Ok")
        self._ok_button.setEnabled(False)
        self._ok_button.pressed.connect(self._on_ok)

        hbox.addStretch(2)
        hbox.addWidget(cancel_button)
        hbox.addWidget(self._ok_button)

        vbox.addLayout(hbox)

        # set current paths and update icon state
        self._fns_line_edit.setText(self.fns_path)
        self._asm_line_edit.setText(self.asm_path)

    def _check_fns_file(self, path: str):
        self._fns_is_good = False
        self._check_ok_button()

        new_path = Path(path)

        if not new_path.is_file():
            self._fns_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxCritical))
            self._fns_check_icon.setToolTip("Given path is not a file/does not exist.")
            return

        try:
            self._check_fns_content(new_path)
        except Exception as e:
            self._fns_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxWarning))
            self._fns_check_icon.setToolTip(str(e))
            return

        self._fns_is_good = True
        self._fns_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_DialogYesButton))
        self._fns_check_icon.setToolTip("")

        self._check_ok_button()

    @staticmethod
    def _check_fns_content(new_path: Path):
        lines_to_check = 10

        for line in new_path.open().readlines():
            if line.startswith(";"):
                continue

            if not line.strip():
                continue

            try:
                name, value = line.split("=")

                if not value.strip().startswith("$"):
                    raise ValueError()

            except ValueError:
                raise ValueError("Didn't find lines in the form of 'name = $1234'. File might be wrongly formatted.")

            lines_to_check -= 1

            if lines_to_check == 0:
                break

        return True

    def _check_asm_file(self, path: str):
        self._asm_is_good = False
        self._check_ok_button()

        new_path = Path(path)

        if not new_path.is_file():
            self._asm_check_icon.setToolTip("Given path is not a file/does not exist.")
            self._asm_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxCritical))
            return

        try:
            self._check_asm_location(new_path)
        except Exception as e:
            self._asm_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxWarning))
            self._asm_check_icon.setToolTip(str(e))
            return

        self._asm_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_DialogYesButton))
        self._asm_check_icon.setToolTip("")

        self._asm_is_good = True

        self._check_ok_button()

    @staticmethod
    def _check_asm_location(path: Path):
        prg_path = path.parent / "PRG" / "prg000.asm"

        if not prg_path.exists():
            raise ValueError(f"Couldn't find {prg_path}. Make sure your smb3.asm is in the assembly directory.")

    def _check_ok_button(self):
        self._ok_button.setEnabled(self._fns_is_good and self._asm_is_good)

    def _on_ok(self):
        self.fns_path = self._fns_line_edit.text()
        self.asm_path = self._asm_line_edit.text()

        self.accept()

    def _get_fns_file(self):
        fns_file, _ = QFileDialog.getOpenFileName(self, "Open FNS File", filter=FNS_FILE_FILTER)

        if not fns_file:
            return

        self._fns_line_edit.setText(fns_file)

    def _get_asm_file(self):
        asm_file, _ = QFileDialog.getOpenFileName(self, "Open smb3.asm File", filter=SMB3_ASM_FILE_FILTER)

        if not asm_file:
            return

        self._asm_line_edit.setText(asm_file)


if __name__ == "__main__":
    app = QApplication()

    dialog = FnsAsmLoadDialog(None)

    dialog.show()

    app.exec()
