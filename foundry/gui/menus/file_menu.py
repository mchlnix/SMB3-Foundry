"""File-menu workflows for ROM, ASM, FNS, and M3L boundaries.

This module owns the editor actions that cross the boundary between the live
session and file-backed formats. It keeps ROM opens/saves, ASM round-trips,
FNS imports, and standalone M3L snapshots in one place so the main window can
delegate file I/O without duplicating dialog and refresh behavior.

See Also
--------
foundry.gui.MainWindow
    Hosts this menu inside the top-level editor shell.
foundry.gui.m3l
    Provides standalone level snapshot persistence used by several actions.
"""

from pathlib import Path

from PySide6.QtGui import QAction, QCursor, QGuiApplication, Qt
from PySide6.QtWidgets import QMenu, QMessageBox

from foundry import NO_PARENT, icon
from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.asm import (
    load_asm_filename,
    load_asm_level,
    make_fns_file_absolute,
    save_asm,
    save_asm_filename,
)
from foundry.gui.dialogs.fns_asm_load_dialog import FnsAsmLoadDialog
from foundry.gui.m3l import save_m3l, save_m3l_filename
from foundry.gui.settings import Settings
from smb3parse.constants import update_global_offsets


class FileMenu(QMenu):
    """Own the file-oriented editor actions for one editor session.

    The file menu is the bridge between the live level model and the editor's
    import and export formats. It keeps ROM save actions, standalone `M3L`
    snapshots, ASM round-trips, and FNS-driven global-offset updates in one
    place so the main window can expose those workflows without duplicating the
    file-dialog and refresh logic.

    Parameters
    ----------
    level_ref : LevelRef
        Shared reference to the active level and its selection state.
    settings : Settings
        Persistent editor settings, including the default directory used by
        file dialogs.
    title : str, optional
        Menu title shown in the main window.

    Attributes
    ----------
    level_ref : LevelRef
        Active level reference used by import and export actions.
    settings : Settings
        Settings store queried for default paths and dialog defaults.
    open_rom_action : QAction
        Action that opens a ROM file into the editor.
    save_rom_action : QAction
        Action that writes the loaded ROM back to disk.
    save_rom_as_action : QAction
        Action that writes the loaded ROM to a new file.
    reload_rom_action : QAction
        Action that reloads the open ROM from disk.
    open_m3l_action : QAction
        Action that loads a standalone `M3L` level snapshot.
    save_m3l_action : QAction
        Action that exports the active level as `M3L`.
    open_level_asm_action : QAction
        Action that imports level layout ASM into the active level.
    save_level_asm_action : QAction
        Action that exports the active level layout as ASM.
    import_enemy_asm_action : QAction
        Action that imports enemy ASM.
    export_enemy_asm_action : QAction
        Action that exports enemy ASM.
    import_fns_action : QAction
        Action that reloads global ASM offsets from an FNS file.
    settings_action : QAction
        Action that opens the editor settings dialog.
    exit_action : QAction
        Action that closes the application.
    """

    def __init__(self, level_ref: LevelRef, settings: Settings, title="&File"):
        """Create the file menu for the active editor session.

        The constructor groups ROM, ASM, M3L, and FNS workflows into one menu
        so the main window can expose file-format transitions without carrying
        each dialog and path-handling detail itself.

        Parameters
        ----------
        level_ref : LevelRef
            Shared reference to the active level and its selection state.
        settings : Settings
            Persistent editor settings, including the default directory used by
            file dialogs.
        title : str, optional
            Menu title shown in the main window.
        """
        super(FileMenu, self).__init__(title)

        self.level_ref = level_ref
        self.settings = settings

        self.triggered.connect(self._on_trigger)

        self.open_rom_action = self.addAction("Open ROM")
        self.open_rom_action.setIcon(icon("folder.svg"))

        self.addSeparator()

        self.save_rom_action = self.addAction("Save ROM")
        self.save_rom_action.setIcon(icon("save.svg"))
        self.save_rom_action.setShortcut(Qt.Modifier.CTRL | Qt.Key.Key_S)

        self.save_rom_as_action = self.addAction("Save ROM as ...")
        self.save_rom_as_action.setIcon(icon("save.svg"))

        self.addSeparator()

        self.reload_rom_action = self.addAction("Reload ROM")
        self.reload_rom_action.setIcon(icon("refresh-cw.svg"))

        self.addSeparator()

        m3l_menu = QMenu("M3L")
        m3l_menu.setIcon(icon("file.svg"))

        self.open_m3l_action = m3l_menu.addAction("Open M3L")
        self.open_m3l_action.setIcon(icon("folder.svg"))

        self.save_m3l_action = m3l_menu.addAction("Save M3L")
        self.save_m3l_action.setIcon(icon("save.svg"))

        asm_menu = QMenu("ASM")
        asm_menu.setIcon(icon("cpu.svg"))

        self.open_level_asm_action = asm_menu.addAction("Open Level")
        self.open_level_asm_action.setIcon(icon("folder.svg"))
        # open_level_asm.triggered.connect(self.on_open_asm)

        self.save_level_asm_action = asm_menu.addAction("Save Level")
        self.save_level_asm_action.setIcon(icon("save.svg"))

        asm_menu.addSeparator()

        self.import_enemy_asm_action = asm_menu.addAction("Import Enemies")
        self.import_enemy_asm_action.setIcon(icon("upload.svg"))

        self.export_enemy_asm_action = asm_menu.addAction("Export Enemies")
        self.export_enemy_asm_action.setIcon(icon("download.svg"))

        asm_menu.addSeparator()

        self.import_fns_action = asm_menu.addAction("Import FNS Addresses")
        self.import_fns_action.setIcon(icon("upload.svg"))

        self.addMenu(m3l_menu)
        self.addMenu(asm_menu)

        self.addSeparator()

        self.settings_action = self.addAction("Editor Settings")
        self.settings_action.setIcon(icon("sliders.svg"))

        self.addSeparator()

        self.exit_action = self.addAction("Exit")
        self.exit_action.setIcon(icon("power.svg"))

    def _on_trigger(self, action: QAction):
        """Dispatch handled submenu actions to their file workflow.

        Parameters
        ----------
        action : QAction
            Triggered action from this menu or one of its submenus.
        """
        if action is self.save_level_asm_action:
            self.on_save_level_asm()
        elif action is self.export_enemy_asm_action:
            self.on_save_enemy_asm()
        elif action is self.open_level_asm_action:
            self.on_open_level_asm()
        elif action is self.save_m3l_action:
            self.on_save_m3l()
        elif action is self.import_fns_action:
            self.on_fns_import()

    def on_open_level_asm(self):
        """Load level-layout ASM into the active level.

        The dialog starts in the configured default directory. When the user
        selects a file, the parsed ASM is applied directly to the level
        model.
        """
        if not (pathname := load_asm_filename("Level ASM", self.settings.value("editor/default_dir_path"))):
            return

        load_asm_level(pathname, self.level_ref.level)

    def on_save_level_asm(self):
        """Export the loaded level layout as ASM.

        The suggested filename follows the active level name so layout exports
        stay aligned with other per-level artifacts in the default directory.
        """
        suggested_file = f"{self.settings.value('editor/default_dir_path')}/{self.level_ref.name}.asm"

        level_asm, _ = self.level_ref.level.to_asm()

        self.save_asm(suggested_file, level_asm, "Level ASM")

    def on_save_enemy_asm(self):
        """Export the loaded level's enemy data as ASM.

        Enemy data is written separately from layout ASM because Foundry and
        SMB3 treat those streams as distinct assets.
        """
        suggested_file = f"{self.settings.value('editor/default_dir_path')}/{self.level_ref.name}_enemy.asm"

        _, enemy_asm = self.level_ref.level.to_asm()

        self.save_asm(suggested_file, enemy_asm, "Enemy ASM")

    @staticmethod
    def save_asm(suggested_file: str, asm: str, what: str):
        """Write an ASM export after confirming the destination path.

        The helper keeps level-layout and enemy-data exports on the same save
        path workflow while leaving the caller responsible for generating the
        assembly text.

        Parameters
        ----------
        suggested_file : str
            Initial path offered by the save dialog.
        asm : str
            Assembly source to write.
        what : str
            User-facing label shown by the save dialog and error reporting.
        """
        if not (pathname := save_asm_filename(what, suggested_file)):
            return

        save_asm(what, pathname, asm)

    def on_save_m3l(self):
        """Export the loaded level to the standalone `M3L` format.

        `M3L` snapshots preserve the level independent of its ROM slot, which
        makes the format useful for external sharing and detached editing.
        """
        suggested_file = self.settings.value("editor/default_dir_path") + "/" + self.level_ref.name + ".m3l"

        if not (pathname := save_m3l_filename(suggested_file)):
            return

        m3l_bytes = self.level_ref.level.to_m3l()

        save_m3l(pathname, m3l_bytes)

    def on_fns_import(self):
        """Import FNS-derived ASM offsets and refresh editor state.

        This workflow lets the editor follow an external SMB3 ASM checkout. A
        successful import updates the global offset table, records the chosen
        ASM and FNS paths on `ROM`, and triggers a graphics reset so later
        decoding uses the new offsets.
        """
        open_dialog = FnsAsmLoadDialog(NO_PARENT, ROM.fns_path, ROM.smb3_asm_path)
        if open_dialog.exec() == FnsAsmLoadDialog.DialogCode.Rejected:
            return

        fns_path = Path(open_dialog.fns_path)
        asm_path = Path(open_dialog.asm_path)

        if self.update_globals_from_fns(asm_path, fns_path):
            QMessageBox.information(NO_PARENT, "Update complete", "Successfully updated the ASM globals.")

    # TODO kinda clunky that this is here
    def update_globals_from_fns(self, asm_path: Path, fns_path: Path):
        """Refresh global ASM offsets from an FNS file.

        This is the boundary where external ASM project metadata becomes live
        Foundry decode state for later ROM parsing, graphics loading, and ASM
        import/export workflows.

        Parameters
        ----------
        asm_path : Path
            Root path of the ASM checkout selected by the user.
        fns_path : Path
            FNS file selected by the user.

        Returns
        -------
        bool
            `True` when the offsets were updated successfully, otherwise
            `False`.
        """
        try:
            QGuiApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            absolute_fns_path = make_fns_file_absolute(fns_path, asm_path)

            update_global_offsets(absolute_fns_path)

            absolute_fns_path.unlink(missing_ok=True)

            ROM.fns_path = str(fns_path)
            ROM.smb3_asm_path = str(asm_path)

        except Exception as e:
            QMessageBox.critical(NO_PARENT, "Failed updating globals", str(e))
            return False

        finally:
            QGuiApplication.restoreOverrideCursor()

        ROM.reset_graphics()

        if self.level_ref:
            self.level_ref.data_changed.emit()

        return True
