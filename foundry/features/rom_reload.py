from hashlib import md5
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, Signal, SignalInstance


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
