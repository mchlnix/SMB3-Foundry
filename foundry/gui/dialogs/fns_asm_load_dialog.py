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
from foundry.gui.localization import tr

TR_CONTEXT = "FnsAsmLoadDialog"
MISSING_FILE_MESSAGE = "Given path is not a file/does not exist."
MISSING_FILE_KEY = "error.missing_file_path"
BAD_FNS_FORMAT_MESSAGE = "Didn't find lines in the form of 'name = $1234'. File might be wrongly formatted."
BAD_FNS_FORMAT_KEY = "error.bad_fns_format"
MISSING_PRG_MESSAGE = "Couldn't find {prg_path}. Make sure your smb3.asm is in the assembly directory."
MISSING_PRG_KEY = "error.missing_prg_asm"


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
    _asm_status_tooltip_args : dict[str, object]
        Format arguments for the active ASM validation tooltip.
    _asm_status_tooltip_key : str
        Stable catalog key for the active ASM validation tooltip.
    _asm_status_tooltip_source : str
        English ASM validation tooltip fallback text.
    _cancel_button : QPushButton
        Button that rejects the dialog without changing staged paths.
    _explanation_label : QLabel
        Wrapped label explaining why both FNS and ASM files are required.
    _fns_check_icon : QLabel
        Status icon for FNS validation.
    _fns_is_good : bool
        Whether the FNS path passes validation.
    _fns_line_edit : QLineEdit
        Editable FNS path field.
    _fns_open_button : QPushButton
        Button that opens the FNS file picker.
    _fns_status_tooltip_args : dict[str, object]
        Format arguments for the active FNS validation tooltip.
    _fns_status_tooltip_key : str
        Stable catalog key for the active FNS validation tooltip.
    _fns_status_tooltip_source : str
        English FNS validation tooltip fallback text.
    _ok_button : QPushButton
        Confirmation button enabled only when both files validate.
    _question_label : QLabel
        Information icon that owns the long explanatory tooltip.
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
        super().__init__(parent, title=tr(TR_CONTEXT, "update_globals_from_files", "Update Globals from files"))

        self.fns_path = cur_fns_file
        self._fns_is_good = False
        self._fns_status_tooltip_key = ""
        self._fns_status_tooltip_source = ""
        self._fns_status_tooltip_args = {}

        self.asm_path = current_asm_file
        self._asm_is_good = False
        self._asm_status_tooltip_key = ""
        self._asm_status_tooltip_source = ""
        self._asm_status_tooltip_args = {}

        vbox = QVBoxLayout(self)

        hbox = QHBoxLayout()

        self._explanation_label = QLabel()
        self._explanation_label.setWordWrap(True)
        self._explanation_label.setMargin(5)

        self._question_label = QLabel()
        self._question_label.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxInformation))

        hbox.addWidget(self._explanation_label)
        hbox.addWidget(self._question_label)

        vbox.addLayout(hbox)

        self._fns_line_edit = QLineEdit()
        self._fns_line_edit.textChanged.connect(self._check_fns_file)

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

        self._cancel_button = QPushButton()
        self._cancel_button.pressed.connect(self.reject)

        self._ok_button = QPushButton()
        self._ok_button.setEnabled(False)
        self._ok_button.pressed.connect(self._on_ok)

        hbox.addStretch(2)
        hbox.addWidget(self._cancel_button)
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
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Refresh translated ASM-loading text without changing staged files.

        The line-edit contents, validation booleans, and accepted path fields
        are stable workflow data for the later global remapping pass. This
        method updates Qt labels, placeholders, buttons, and cached validation
        tooltips so live language switching mirrors the same FNS/``smb3.asm``
        file-validity state the user already sees, without reparsing the files
        or changing the ROM-offset mapping inputs.
        """
        self.setWindowTitle(tr(TR_CONTEXT, "update_globals_from_files", "Update Globals from files"))
        self._explanation_label.setText(
            tr(TR_CONTEXT, "prompt.fns_asm_files", "Provide an FNS file and the smb3.asm file from your project.")
        )
        self._question_label.setToolTip(self._question_tooltip_text())
        self._fns_line_edit.setPlaceholderText(tr(TR_CONTEXT, "path_to_fns_file", "Path to FNS file."))
        self._asm_line_edit.setPlaceholderText(tr(TR_CONTEXT, "path_to_smb3_asm_file", "Path to smb3.asm file."))
        self._cancel_button.setText(tr("Common", "cancel", "Cancel"))
        self._ok_button.setText(tr("Common", "ok_title", "Ok"))
        self._refresh_status_tooltips()

    @staticmethod
    def _question_tooltip_text() -> str:
        """Build the translated help text for FNS/ASM remapping.

        The tooltip is display-only guidance for the dialog's information icon.
        It explains the SMB3 assembly boundary that motivates the file pair:
        FNS labels describe NES memory addresses, while the matching
        ``smb3.asm`` tree lets Foundry resolve those labels back to ROM file
        offsets before global editor addresses are updated.

        Returns
        -------
        str
            Multi-line tooltip explaining why Foundry needs both the compiled
            FNS label output and the source ASM tree to map labels to ROM
            offsets.
        """
        return tr(
            TR_CONTEXT,
            "help.fns_asm_files",
            "A FNS file is a by-product of compiling a Rom file from assembly code.\nIt has all the labels used in the code and their positions as they would be in the NES's memory.\nSome of these labels are used by the editor to find important data, like levels, palette colors, etc.\nThe editor, however, needs to know where the code these labels describe, is in the Rom file.\nBy default the editor ships with these addresses for the unaltered US SMB3 Rom, but if you have\nmade changes to the code, and things moved around, those addresses might not be valid anymore.\nFor that purpose, the editor needs the FNS file and your smb3.asm file as well, to generate the location\nin the Rom for every label in the FNS file.",
        )

    def _refresh_status_tooltips(self) -> None:
        """Rebuild validation tooltips from cached validation state.

        File checks store stable tooltip keys, English fallback text, and any
        formatting arguments when FNS or ``smb3.asm`` validation changes. Live
        language switching uses that cached state to retranslate the status
        icons without touching the line edits, reparsing the selected files, or
        changing the booleans that control the OK button. That keeps display
        text in sync with the active catalog while preserving the already-staged
        remapping inputs.
        """
        if self._fns_status_tooltip_key:
            self._fns_check_icon.setToolTip(
                tr(TR_CONTEXT, self._fns_status_tooltip_key, self._fns_status_tooltip_source).format(
                    **self._fns_status_tooltip_args
                )
            )

        if self._asm_status_tooltip_key:
            self._asm_check_icon.setToolTip(
                tr(TR_CONTEXT, self._asm_status_tooltip_key, self._asm_status_tooltip_source).format(
                    **self._asm_status_tooltip_args
                )
            )

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
            self._fns_status_tooltip_key = MISSING_FILE_KEY
            self._fns_status_tooltip_source = MISSING_FILE_MESSAGE
            self._fns_status_tooltip_args = {}
            self._refresh_status_tooltips()
            return

        try:
            self._check_fns_content(new_path)
        except Exception as e:
            self._fns_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxWarning))
            self._fns_status_tooltip_key = BAD_FNS_FORMAT_KEY if isinstance(e, ValueError) else ""
            self._fns_status_tooltip_source = BAD_FNS_FORMAT_MESSAGE if isinstance(e, ValueError) else ""
            self._fns_status_tooltip_args = {}
            self._fns_check_icon.setToolTip(str(e))
            self._refresh_status_tooltips()
            return

        self._fns_is_good = True
        self._fns_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_DialogYesButton))
        self._fns_status_tooltip_key = ""
        self._fns_status_tooltip_source = ""
        self._fns_status_tooltip_args = {}
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
                raise ValueError(tr(TR_CONTEXT, BAD_FNS_FORMAT_KEY, BAD_FNS_FORMAT_MESSAGE))

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
            self._asm_status_tooltip_key = MISSING_FILE_KEY
            self._asm_status_tooltip_source = MISSING_FILE_MESSAGE
            self._asm_status_tooltip_args = {}
            self._refresh_status_tooltips()
            self._asm_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxCritical))
            return

        try:
            self._check_asm_location(new_path)
        except Exception as e:
            self._asm_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxWarning))
            self._asm_status_tooltip_key = MISSING_PRG_KEY if isinstance(e, ValueError) else ""
            self._asm_status_tooltip_source = MISSING_PRG_MESSAGE if isinstance(e, ValueError) else ""
            self._asm_status_tooltip_args = {"prg_path": new_path.parent / "PRG" / "prg000.asm"}
            self._asm_check_icon.setToolTip(str(e))
            self._refresh_status_tooltips()
            return

        self._asm_check_icon.setPixmap(self.style().standardPixmap(QStyle.StandardPixmap.SP_DialogYesButton))
        self._asm_status_tooltip_key = ""
        self._asm_status_tooltip_source = ""
        self._asm_status_tooltip_args = {}
        self._asm_check_icon.setToolTip("")

        self._asm_is_good = True

        self._check_ok_button()

    @staticmethod
    def _check_asm_location(path: Path):
        """Verify that the ASM file lives inside a usable SMB3 source tree.

        The lightweight check looks for the neighboring ``PRG/prg000.asm`` file
        that Foundry's later remapping code expects when translating label
        addresses back into ROM offsets. It intentionally leaves full parsing
        to the ASM loading workflow and only guards the dialog's OK state.

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
            raise ValueError(tr(TR_CONTEXT, MISSING_PRG_KEY, MISSING_PRG_MESSAGE).format(prg_path=prg_path))

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
        fns_file, _ = QFileDialog.getOpenFileName(
            self, tr(TR_CONTEXT, "open_fns_file", "Open FNS File"), filter=FNS_FILE_FILTER
        )

        if not fns_file:
            return

        self._fns_line_edit.setText(fns_file)

    def _get_asm_file(self):
        """Prompt for ``smb3.asm`` and stage it in the line edit.

        Writing the chosen path into the line edit reuses the same validation
        flow as manual text entry.
        """
        asm_file, _ = QFileDialog.getOpenFileName(
            self, tr(TR_CONTEXT, "open_smb3_asm_file", "Open smb3.asm File"), filter=SMB3_ASM_FILE_FILTER
        )

        if not asm_file:
            return

        self._asm_line_edit.setText(asm_file)


if __name__ == "__main__":
    app = QApplication()

    dialog = FnsAsmLoadDialog(None)

    dialog.show()

    app.exec()
