from contextlib import contextmanager
from hashlib import md5
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import QFileSystemWatcher, Signal, SignalInstance
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QApplication, QMessageBox

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef
from smb3parse.levels import HEADER_LENGTH

if TYPE_CHECKING:
    from foundry.gui.menus.file_menu import FileMenu


class RomWatcherMixin:
    rom_content_changed: SignalInstance = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_watcher = QFileSystemWatcher()
        self._file_watcher.fileChanged.connect(self.on_file_changed)

        self._current_path = Path()

        self._last_accepted_hash: str = ""
        """
        A md5 has representing the last known state of the contents of the ROM. We only want to send a signal, if the
        content changes.
        """

        self._rom_watcher_enabled = True

    def on_file_changed(self):
        new_hash = self._hash_current_file()

        if new_hash != self._last_accepted_hash and self._rom_watcher_enabled:
            self.rom_content_changed.emit()

        self._last_accepted_hash = new_hash

    def set_rom_path_to_watch(self, path: Path):
        self._clear()

        self._update_path(path)

        self._update_accepted_hash()

    def _update_path(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"ROM file not found at {path}")

        self._current_path = path
        self._file_watcher.addPath(str(path))

    def _update_accepted_hash(self):

        self._last_accepted_hash = self._hash_current_file()

    def _hash_current_file(self) -> str:
        if not self._current_path.exists():
            raise FileNotFoundError(f"ROM file not found at {self._current_path}")

        return md5(self._current_path.read_bytes(), usedforsecurity=False).hexdigest()

    def _clear(self):
        for path in self._file_watcher.files():
            self._file_watcher.removePath(path)

    @contextmanager
    def _rom_watcher_disabled(self):
        status_before = self._rom_watcher_enabled

        self._rom_watcher_enabled = False

        try:
            yield
        finally:
            # flush all events, including queued file changes, from before this was called, but ready to trigger after
            QApplication.processEvents()
            self._rom_watcher_enabled = status_before


class RomHotSwapMixin:
    # members of FoundryMainWindow
    level_ref: LevelRef
    undo_stack: QUndoStack
    update_level: Callable
    on_open_rom: Callable
    file_menu: "FileMenu"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__original_level_bytes = bytes()
        self.__original_enemy_bytes = bytes()
        self.__original_object_set = 0

        self.__undo_stack_index_before_reload = 0

    def prepare_level_reload(self):
        self._unwind_undo_stack()
        original_level_data = self.level_ref.level.to_bytes()

        (lvl_address, lvl_data), (enemy_address, enemy_data) = original_level_data

        # our level object reorders level objects, so get the original data from the ROM
        self.__original_level_bytes = ROM().read(lvl_address, len(lvl_data))
        self.__original_enemy_bytes = ROM().read(enemy_address, len(enemy_data))
        self.__original_object_set = self.level_ref.level.object_set_number

    def _unwind_undo_stack(self):
        self.__undo_stack_index_before_reload = self.undo_stack.index()

        index_at_last_save = self.undo_stack.cleanIndex()

        if index_at_last_save == -1:
            index_at_last_save = 0

        # unwind undo stack to get original level data
        self.undo_stack.setIndex(index_at_last_save)

    def hotswap_roms(self):
        needs_level_reload = bool(self.level_ref) and self.level_ref.level.attached_to_rom

        if needs_level_reload:
            self.prepare_level_reload()

        asm_path_before_reload = Path(ROM.smb3_asm_path)
        fns_path_before_reload = Path(ROM.fns_path)

        self.on_open_rom(Path(ROM.path), check_for_asm_files=False, close_current_level=False, try_opening_level=False)

        if asm_path_before_reload.is_file() and fns_path_before_reload.is_file():
            ROM.smb3_asm_path = str(asm_path_before_reload)
            ROM.fns_path = str(fns_path_before_reload)

            self.file_menu.update_globals_from_fns(asm_path_before_reload, fns_path_before_reload)

        if needs_level_reload:
            self.execute_level_reload()

    def execute_level_reload(self):
        # find the level data in the ROM again, since it might have been moved
        new_lvl_address, new_enemy_address = self._find_current_level_in_new_rom()

        if -1 in (new_lvl_address, new_enemy_address):
            QMessageBox.critical(
                self,
                "Problem after reloading the ROM",
                "Could not find the original level data in the updated ROM.\n\n"
                "Detaching the level for now, you can attach it again manually.",
            )

            self.level_ref.level.detach_from_rom()
            return

        # open the level again
        self.update_level("", new_lvl_address, new_enemy_address, self.__original_object_set)

        self._rewind_undo_stack()

    def _find_current_level_in_new_rom(self) -> tuple[int, int]:
        new_lvl_address = -1

        # split original data and look for the level objects first
        original_header_bytes = self.__original_level_bytes[:HEADER_LENGTH]
        original_level_object_bytes = self.__original_level_bytes[HEADER_LENGTH:]

        # in case there are multiple levels with the same level objects, we continue looking if the header doesn't match
        search_start = 0

        while True:
            new_level_object_address = ROM().find(original_level_object_bytes, start=search_start)

            # did not find the level object data at all, so we have to detach it
            if new_level_object_address == -1:
                return -1, -1

            search_start = new_level_object_address + 1

            new_level_header_address = new_level_object_address - HEADER_LENGTH
            new_header_bytes = ROM().read(new_level_header_address, HEADER_LENGTH)

            # we can only compare data unrelated to the jump destination because it might have also changed,
            # so we zero out the addresses in the first two bytes and the object set in byte #6
            header_comparison_mask = 0x00_00_00_00_FF_FF_F0_FF_FF

            original_header_comp_value = int.from_bytes(original_header_bytes, "big") & header_comparison_mask
            new_header_comp_value = int.from_bytes(new_header_bytes, "big") & header_comparison_mask

            # if the header values don't match, we found a different level with the same level objects (hammer bros?)
            if original_header_comp_value != new_header_comp_value:
                continue
            else:
                new_lvl_address = new_level_header_address
                break

        # do the same for the enemy data
        new_enemy_address = ROM().find(self.__original_enemy_bytes)

        return new_lvl_address, new_enemy_address

    def _rewind_undo_stack(self):
        self.undo_stack.setIndex(0)

        # reapply all the undo commands
        while self.undo_stack.canRedo() and self.undo_stack.index() < self.__undo_stack_index_before_reload:
            self.undo_stack.redo()
