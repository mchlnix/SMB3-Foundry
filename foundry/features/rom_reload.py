from hashlib import md5
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QFileSystemWatcher, Signal, SignalInstance
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QMessageBox

from foundry.game.File import ROM
from foundry.game.level.LevelRef import LevelRef


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


class RomHotSwapMixin:
    # members of FoundryMainWindow
    level_ref: LevelRef
    undo_stack: QUndoStack
    _protect_undo_stack: bool
    _rom_watcher_enabled: bool
    update_level: Callable
    on_open_rom: Callable

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
        self._protect_undo_stack = True

        needs_level_reload = bool(self.level_ref) and self.level_ref.level.attached_to_rom

        if needs_level_reload:
            self.prepare_level_reload()

        self.on_open_rom(Path(ROM.path), close_current_level=False, try_opening_level=False)

        if needs_level_reload:
            self.execute_level_reload()

        self._protect_undo_stack = False

    def execute_level_reload(self):
        # find the level data in the ROM again, since it might have moved
        new_lvl_address = ROM.rom_data.find(self.__original_level_bytes)

        # do the same for the enemy data
        new_enemy_address = ROM.rom_data.find(self.__original_enemy_bytes)

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

    def _rewind_undo_stack(self):
        self.undo_stack.setIndex(0)

        # reapply all the undo commands
        while self.undo_stack.canRedo() and self.undo_stack.index() < self.__undo_stack_index_before_reload:
            self.undo_stack.redo()
