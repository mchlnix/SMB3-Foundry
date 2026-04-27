"""Collect ASM remapping files for features that depend on custom disassemblies.

This module owns the dialog that asks for an FNS label file and the matching
``smb3.asm`` source file when Foundry needs to translate symbolic labels from a
custom SMB3 build back into ROM offsets. It is the GUI boundary between
user-supplied disassembly artifacts and the later remapping workflow that
updates global addresses used by ASM-aware editor features.

See Also
--------
foundry.gui.dialogs.SettingsDialog
    Stores the policy that decides when ASM-aware loading prompts should appear.
foundry.features.rom_reload
    Neighboring ROM-management workflow that reacts to external file changes.
"""

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
from foundry.game.File import ROM
from foundry.gui.asm import asm_paths_from_rom_path
from foundry.gui.dialogs.CustomDialog import CustomDialog


class FnsAsmLoadDialog(CustomDialog):
    """Collect and validate FNS and ``smb3.asm`` paths for global remapping.

    Foundry uses this dialog when ASM-aware features need symbol locations from
    a custom disassembly build. The dialog validates both files, suggests
    plausible defaults near the active ROM, and only enables confirmation once
    both inputs look usable.

    Parameters
    ----------
    parent : QWidget | None
        Parent Qt widget that owns this object.
    cur_fns_file : str, optional
        Path to the existing FNS file, if one was already chosen.
    current_asm_file : str, optional
        Path to the existing ASM file, if one was already chosen.

    Attributes
    ----------
    _asm_check_icon : QLabel
        Status icon for ASM validation.
    _asm_is_good : bool
        Whether the ASM path passes validation.
    _asm_line_edit : QLineEdit
        Editable ASM path field.
    _asm_open_button : QPushButton
        Button that opens the ASM file picker.
    _fns_check_icon : QLabel
        Status icon for FNS validation.
    _fns_is_good : bool
        Whether the FNS path passes validation.
    _fns_line_edit : QLineEdit
        Editable FNS path field.
    _fns_open_button : QPushButton
        Button that opens the FNS file picker.
    _ok_button : QPushButton
        Confirmation button enabled only when both files validate.
    asm_path : str
        Selected ASM path.
    fns_path : str
        Selected FNS path.

    Notes
    -----
    The dialog is part of Foundry's compatibility boundary with custom SMB3
    disassemblies. FNS labels alone are not enough; Foundry also needs the ASM
    source layout to translate NES-memory labels back into ROM file offsets.
    """

    def __init__(self, parent, cur_fns_file: str = "", current_asm_file: str = ""):
        """Build the file-picking and validation UI.

        Construction follows the same staged flow the user sees at runtime:
        build the explanatory text, create paired line-edit, status-icon, and
        browse-button rows for the FNS and ASM files, add the guarded OK button
        row, then seed both path fields from previously stored values or from
        plausible files near the active ROM. Setting those line edits triggers
        the validation handlers immediately, so the dialog opens with both the
        visible status icons and the OK-button state already synchronized to the
        best candidate files. That means the constructor is not just widget
        setup: it is also the dialog's initial validation pass, because later
        global-remapping workflows depend on these fields already carrying the
        accepted or rejected state that the user sees before they browse.

        Parameters
        ----------
        parent : QWidget | None
            Parent Qt widget that owns this object.
        cur_fns_file : str, optional
            Path to the existing FNS file, if one was already chosen.
        current_asm_file : str, optional
            Path to the existing ASM file, if one was already chosen.
        """
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

        # set current paths
        rom_base_path = Path(ROM.path).parent
        rom_name = Path(ROM.path).name.removesuffix(".nes")
        backup_asm_path, backup_fns_path = asm_paths_from_rom_path(rom_base_path)

        if not Path(self.fns_path).is_file() and backup_fns_path.is_file():
            self.fns_path = str(backup_fns_path)

        if not Path(self.asm_path).is_file() and backup_asm_path.is_file():
            self.asm_path = str(rom_base_path / f"{rom_name}.asm")

        self._fns_line_edit.setText(self.fns_path)
        self._asm_line_edit.setText(self.asm_path)

    def _check_fns_file(self, path: str):
        """Validate the chosen FNS file and update the status icon.

        Validation first pessimistically disables acceptance, then walks
        through the same promotion path the dialog uses for both file rows:
        reject missing files, attempt a lightweight content check, show a
        warning icon when parsing fails, and only restore the success icon and
        re-enable the OK button once both staged files validate together. This
        makes the method part of the dialog's overall gating workflow rather
        than a standalone filesystem check.

        Parameters
        ----------
        path : str
            Filesystem path entered for the FNS file.
        """
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
        """Verify that an FNS file begins with plausible label assignments.

        The dialog only samples the first non-comment label lines because it is
        trying to reject obviously wrong files before the later global-remapping
        workflow does the full parse.

        Parameters
        ----------
        new_path : Path
            Path to the candidate FNS file.

        Returns
        -------
        bool
            True when the FNS content matches the expected format.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
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
        """Validate the chosen ASM file and update the status icon.

        The dialog only needs one coarse structural check here: the selected
        ``smb3.asm`` file must sit in an assembly tree that still contains the
        expected ``PRG/prg000.asm`` layout.

        Parameters
        ----------
        path : str
            Filesystem path entered for ``smb3.asm``.
        """
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
        """Verify that the ASM file lives inside a usable SMB3 source tree.

        It supports a focused editor dialog while keeping UI state synchronized with the model. The method delegates lower-level work while keeping the public workflow focused.

        Parameters
        ----------
        path : Path
            Path to the selected ``smb3.asm`` file.

        Raises
        ------
        ValueError
            If the input data or current state is invalid.
        """
        prg_path = path.parent / "PRG" / "prg000.asm"

        if not prg_path.exists():
            raise ValueError(f"Couldn't find {prg_path}. Make sure your smb3.asm is in the assembly directory.")

    def _check_ok_button(self):
        """Enable confirmation only when both ASM inputs validate.

        The dialog keeps the OK button disabled until both status checks have
        promoted their files to a usable state.
        """
        self._ok_button.setEnabled(self._fns_is_good and self._asm_is_good)

    def _on_ok(self):
        """Store the validated paths and accept the dialog.

        Callers read ``fns_path`` and ``asm_path`` after acceptance to update
        Foundry's global ASM remapping state.
        """
        self.fns_path = self._fns_line_edit.text()
        self.asm_path = self._asm_line_edit.text()

        self.accept()

    def _get_fns_file(self):
        """Prompt for an FNS file and stage it in the line edit.

        Writing the chosen path into the line edit reuses the same validation
        flow as manual text entry.
        """
        fns_file, _ = QFileDialog.getOpenFileName(self, "Open FNS File", filter=FNS_FILE_FILTER)

        if not fns_file:
            return

        self._fns_line_edit.setText(fns_file)

    def _get_asm_file(self):
        """Prompt for ``smb3.asm`` and stage it in the line edit.

        Writing the chosen path into the line edit reuses the same validation
        flow as manual text entry.
        """
        asm_file, _ = QFileDialog.getOpenFileName(self, "Open smb3.asm File", filter=SMB3_ASM_FILE_FILTER)

        if not asm_file:
            return

        self._asm_line_edit.setText(asm_file)


if __name__ == "__main__":
    app = QApplication()

    dialog = FnsAsmLoadDialog(None)

    dialog.show()

    app.exec()
