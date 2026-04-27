"""ROM file watching and hot-swap support.

Foundry can keep a level open while the backing ROM changes on disk, which is
important when Scribe or an external build process rewrites the ROM. The watcher
detects meaningful byte changes, while the hot-swap mixin preserves enough
level bytes, object-set metadata, and undo-stack position to reload the ROM and
replay the user's in-editor edits against the refreshed data.

See Also
--------
foundry.features.instaplay
    Another feature that temporarily stages ROM state outside the normal save
    workflow.
foundry.game.level.LevelRef
    Captures the level identity used to reopen the same level after reload.

Examples
--------
The watcher and hot-swap mixins are usually paired on the main window so an
external ROM rewrite can trigger a controlled reload::

    window.set_rom_path_to_watch(Path("game.nes"))
    window.rom_content_changed.connect(window.hotswap_roms)

After the user accepts a detected rewrite, Foundry preserves editor state and
replays it against the new ROM bytes::

    window.prepare_level_reload()
    window.hotswap_roms()
"""

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
    """Detect external changes to the loaded ROM file.

    The watcher tracks one ROM path and hashes the file contents so duplicate
    filesystem notifications do not trigger duplicate reload prompts. Foundry
    temporarily disables this watcher while it writes autosave or save output,
    preventing its own writes from being treated as external edits. The mixin
    only decides whether the ROM bytes changed enough to matter; higher-level
    code chooses whether to prompt the user, hot-swap the ROM, or ignore the
    event. It is the long-lived policy boundary between noisy filesystem
    activity and the editor's narrower concept of an accepted ROM change, so
    save paths, autosave, reopen, and external build workflows can all share
    one file without also sharing one user-facing reaction. Just as important,
    it keeps Qt watcher ownership and accepted-baseline state in one place, so
    future reload features can change prompting or state-restoration behavior
    without also having to duplicate low-level file-notification policy. That
    makes the mixin part of Foundry's larger reliability story: one piece of
    code decides when watched ROM bytes have crossed from background filesystem
    noise into a meaningful external change, and every higher-level workflow
    can build on that same decision instead of inventing competing watcher
    rules.

    Parameters
    ----------
    *args : object
        Positional arguments forwarded to the next base class.
    **kwargs : object
        Keyword arguments forwarded to the next base class.

    Attributes
    ----------
    _current_path : Path
        ROM path currently registered with the file watcher.
    _file_watcher : QFileSystemWatcher
        Qt watcher that emits file-change notifications.
    _last_accepted_hash : str
        Hash of the last ROM contents accepted by Foundry.
    _rom_watcher_enabled : bool
        Whether file-change notifications should emit ``rom_content_changed``.
    rom_content_changed : SignalInstance
        Signal emitted when the watched ROM's accepted hash changes.

    See Also
    --------
    RomHotSwapMixin
        Reopens the ROM and restores editor state after an external change is
        accepted.

    Examples
    --------
    A window that mixes this in can baseline a ROM path and react only when
    the accepted file hash changes::

        window.set_rom_path_to_watch(Path("game.nes"))
        window.rom_content_changed.connect(window.hotswap_roms)

    Duplicate notifications collapse naturally because the watcher compares the
    newly hashed file with the last accepted digest before emitting::

        old_hash = window._last_accepted_hash
        new_hash = window._hash_current_file()
        changed = new_hash != old_hash

    Accepted reload flows move the watcher baseline forward so later prompts
    stay tied to the newest trusted ROM bytes::

        window._update_accepted_hash()
        window.set_rom_path_to_watch(Path("game.nes"))

    Notes
    -----
    The mixin exists to keep file-watcher policy separate from reload policy.
    It owns the "did the watched ROM bytes materially change?" decision and
    preserves enough watcher state for higher-level code to decide whether to
    prompt, ignore the event, or start a hot-swap workflow. That architectural
    split matters over time because autosave, explicit save, reload, and
    external build workflows all touch the same ROM file but do not all deserve
    the same user-facing reaction. Long term, this lets Foundry evolve reload
    behavior without coupling every policy change to raw filesystem watching.
    Future changes should preserve that split: this mixin owns watcher state,
    accepted-baseline policy, and duplicate-event suppression, while caller
    code owns prompts, hot-swap decisions, and state restoration.
    """

    rom_content_changed: SignalInstance = Signal()

    def __init__(self, *args, **kwargs):
        """Create the watcher state used for ROM change detection.

        The mixin forwards base-class construction and then owns the Qt file
        watcher plus the last accepted ROM hash for duplicate-event filtering.

        Parameters
        ----------
        *args : object
            Positional arguments forwarded to the next base class.
        **kwargs : object
            Keyword arguments forwarded to the next base class.
        """
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
        """Emit a change signal when watched ROM bytes changed.

        Qt may emit multiple notifications for one write, so the watched file
        hash is compared with the last accepted hash before notifying callers,
        and Foundry's own save operations can temporarily suppress the signal.
        The method is therefore the policy gate for external rewrites: it turns
        noisy filesystem events into at most one meaningful reload prompt for
        each newly accepted ROM state.

        Notes
        -----
        The watcher never updates editor state directly. Its long-lived
        contract is narrower: decide whether a new digest represents a newly
        accepted ROM state, then leave prompting and hot-swap behavior to the
        higher-level window workflow. That separation lets save code suppress
        watcher output without also needing to own reload prompts or state
        restoration policy, and it keeps "filesystem noise filtering" separate
        from the later decision to reopen the ROM or preserve undo state. The
        method is therefore the steady-state arbitration point between raw file
        notifications and the single user-visible "the ROM changed" event. In
        maintenance terms, this is where watcher policy stops: later code may
        prompt, hot-swap, or ignore, but only after this gate reduces the raw
        filesystem stream to one meaningful change notification. Any future
        change-detection policy should stay here so every external-write path
        still flows through one decision point before the rest of the editor
        reacts.
        """
        new_hash = self._hash_current_file()

        if new_hash != self._last_accepted_hash and self._rom_watcher_enabled:
            self.rom_content_changed.emit()

        self._last_accepted_hash = new_hash

    def set_rom_path_to_watch(self, path: Path):
        """Watch a ROM file and accept its current bytes as baseline.

        Calling this method both redirects the watcher to a new filesystem
        target and resets duplicate-event suppression to that file's present
        bytes. Later change notifications are therefore judged relative to the
        exact ROM the editor most recently agreed to watch, not to a stale
        digest from a previous file.

        Notes
        -----
        This method is the boundary where a new ROM path becomes the single
        authoritative watch target. Clearing old paths before registering the
        new one prevents long-lived watcher state from spanning multiple ROM
        files, and accepting a fresh baseline immediately keeps the next
        external notification anchored to bytes the editor explicitly agreed to
        watch. In practice that means the user can switch ROMs or reopen the
        same ROM without carrying stale watcher history into the new session,
        which keeps later hot-swap prompts attributable to the file the editor
        is actually showing. That makes this the ownership handoff from "the
        window chose a ROM file" to "the watcher now treats these bytes as the
        trusted baseline for all later change prompts." Keeping that handoff
        centralized here prevents reopen, file-switch, and accepted-reload
        workflows from each inventing their own watcher-baseline rules.

        Parameters
        ----------
        path : Path
            ROM file path to watch.
        """
        self._clear()

        self._update_path(path)

        self._update_accepted_hash()

    def _update_path(self, path: Path):
        """Register a ROM path with the Qt file watcher.

        Resetting the watched path here keeps later hash checks and file-change
        notifications tied to the same concrete file on disk, which is the path
        later hot-swap decisions and save suppression logic operate against.

        Parameters
        ----------
        path : Path
            ROM file path to watch.

        Raises
        ------
        FileNotFoundError
            If the expected file cannot be found.

        Examples
        --------
        The digest is the token later compared against the accepted watcher
        state::

            digest = window._hash_current_file()
            changed = digest != window._last_accepted_hash
        """
        if not path.exists():
            raise FileNotFoundError(f"ROM file not found at {path}")

        self._current_path = path
        self._file_watcher.addPath(str(path))

    def _update_accepted_hash(self):
        """Accept the watched file's present bytes as the new baseline.

        This method is the explicit state transition from "the file changed"
        to "these bytes are now trusted." Both initial watch setup and accepted
        reload flows use it to move watched ROM contents into the digest
        that future duplicate-notification checks compare against.

        Notes
        -----
        The mixin centralizes baseline acceptance here so every workflow that
        trusts a ROM rewrite uses the same digest-update rule. That keeps
        initial watch setup, accepted external rewrites, and post-save
        suppression recovery aligned on one notion of the trusted ROM state,
        which is what prevents later file-change prompts from disagreeing about
        which bytes are already accepted. It is the single "commit the watcher
        baseline" step for the mixin, and higher-level reload code should keep
        using this method rather than mutating ``_last_accepted_hash``
        directly. That preserves one durable transition from observed file
        bytes to trusted watcher state.
        """
        self._last_accepted_hash = self._hash_current_file()

    def _hash_current_file(self) -> str:
        """Compute the watched-ROM digest used for change detection.

        The digest is used only to detect local file changes, not for security,
        and it is always taken from the path registered with the
        watcher so emitted notifications correspond to the active ROM target.
        The value becomes the baseline for duplicate-notification suppression in
        ``on_file_changed`` and for accepting a newly watched ROM path in
        ``set_rom_path_to_watch``. In other words, this is the one place where
        the watcher turns the active file on disk into the comparison token the
        rest of the mixin uses to decide whether an external rewrite matters.
        When no path is configured yet, the method returns an empty digest so
        startup and teardown logic can avoid treating "nothing is being
        watched" as a changed ROM. Once a path is active, the method reads the
        current ROM bytes and produces the exact token later stored in
        ``_last_accepted_hash`` and compared in ``on_file_changed``. That makes
        it the handoff from filesystem state to watcher state: disk bytes come
        in here, and duplicate-event suppression plus accepted-baseline updates
        depend on the digest that comes out.

        Returns
        -------
        str
            Hash digest for the watched file contents.

        Raises
        ------
        FileNotFoundError
            If the expected file cannot be found.
        """
        if self._current_path == Path():
            return ""

        if not self._current_path.exists():
            raise FileNotFoundError(f"ROM file not found at {self._current_path}")

        return md5(self._current_path.read_bytes(), usedforsecurity=False).hexdigest()

    def _clear(self):
        """Remove all paths from the Qt file watcher.

        Clearing before a path change or shutdown keeps later file-change
        signals tied to only one ROM target at a time. That prevents old watch
        registrations from leaking into a new reload session and producing
        prompts for a file the editor no longer treats as active.

        Notes
        -----
        Watcher cleanup is intentionally aggressive because stale Qt path
        registrations are harder to reason about than re-registering the one
        path the editor is actively using. Long term, this keeps watcher state
        from outliving the editor workflow that chose the file in the first
        place and avoids cross-talk between one watched ROM session and the
        next. That makes cleanup the reset boundary for the mixin's path state
        and the one place that intentionally forgets prior watch ownership
        before a new session is allowed to become authoritative. Future watcher
        setup code should keep using this reset path instead of partially
        mutating the Qt watcher in place.
        """
        for path in self._file_watcher.files():
            self._file_watcher.removePath(path)

    @contextmanager
    def _rom_watcher_disabled(self):
        """Temporarily suppress ROM watcher notifications.

        Pending Qt events are flushed before restoring the previous state so
        file-change events queued during a Foundry save do not fire afterward.

        Yields
        ------
        None
            Control is yielded while watcher notifications are suppressed.
        """
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
    """Reload a ROM while preserving the active editing session.

    Hot swap supports the workflow where the ROM is rebuilt outside Foundry but
    the user wants to keep the active level and undo history. The mixin captures
    the open level bytes and undo-stack index, unwinds editable changes,
    reloads the ROM, locates the same level in the new ROM, then reapplies the
    undo stack so in-editor edits remain visible.

    Parameters
    ----------
    *args : Any
        Positional arguments forwarded to the next base class.
    **kwargs : Any
        Keyword arguments forwarded to the next base class.

    Attributes
    ----------
    __original_enemy_bytes : bytes
        Enemy bytes captured before unwinding the undo stack.
    __original_level_bytes : bytes
        Level layout bytes captured before unwinding the undo stack.
    __original_object_set : int
        Object set captured before ROM reload.
    __undo_stack_index_before_reload : int
        Undo-stack index restored after the ROM is reloaded.
    file_menu : 'FileMenu'
        File-menu helper used to refresh ASM and FNS-derived globals after
        reload.
    level_ref : LevelRef
        Reference to the open level, if any.
    on_open_rom : Callable
        Main-window ROM-open entry point.
    undo_stack : QUndoStack
        Undo stack whose clean index and command replay are preserved across the
        reload.
    update_level : Callable
        Main-window helper that reopens a level from ROM addresses.

    Notes
    -----
    Hot swap intentionally reloads the ROM from disk instead of patching the
    existing in-memory model. Before that reload, it unwinds the undo stack
    back to the clean state so the reopened level can be matched against ROM
    bytes that external tools actually wrote.

    Examples
    --------
    A change-acceptance flow typically prepares the level state, reloads the
    ROM, and then lets the mixin rebuild the active session::

        self.prepare_level_reload()
        self.hotswap_roms()

    See Also
    --------
    RomWatcherMixin
        Detects when the backing ROM changed and a hot swap may be needed.

    Examples
    --------
    A change-acceptance flow typically prepares the session, reloads the ROM,
    and then reapplies editor state against the refreshed bytes::

        self.prepare_level_reload()
        self.hotswap_roms()

    The preserved session state includes enough information to find the same
    level again in the new ROM and replay the saved undo position::

        self.__undo_stack_index_before_reload = self.undo_stack.index()
        self.execute_level_reload(level_ref)
    """
    level_ref: LevelRef
    undo_stack: QUndoStack
    update_level: Callable
    on_open_rom: Callable
    file_menu: "FileMenu"

    def __init__(self, *args, **kwargs):
        """Initialize cached state used during ROM hot swap.

        The cached bytes and undo index let Foundry reopen the same logical
        level after an external ROM rebuild moves its data elsewhere.

        Parameters
        ----------
        *args : object
            Positional arguments forwarded to the next base class.
        **kwargs : object
            Keyword arguments forwarded to the next base class.
        """
        super().__init__(*args, **kwargs)

        self.__original_level_bytes = bytes()
        self.__original_enemy_bytes = bytes()
        self.__original_object_set = 0

        self.__undo_stack_index_before_reload = 0

    def prepare_level_reload(self):
        """Capture enough pre-reload state to relocate the open level.

        The method rewinds the undo stack to the last clean state, then stores
        the original level bytes, enemy bytes, and object-set number from the
        ROM-backed version of the level. That snapshot is later used to find
        the same level again after the ROM has been reloaded from disk.

        Examples
        --------
        Hot-swap flows call this before reopening the ROM so relocation can
        match the same level afterward::

            self.prepare_level_reload()
            self.hotswap_roms()
        """
        self._unwind_undo_stack()
        original_level_data = self.level_ref.level.to_bytes()

        (lvl_address, lvl_data), (enemy_address, enemy_data) = original_level_data

        # our level object reorders level objects, so get the original data from the ROM
        self.__original_level_bytes = ROM().read(lvl_address, len(lvl_data))
        self.__original_enemy_bytes = ROM().read(enemy_address, len(enemy_data))
        self.__original_object_set = self.level_ref.level.object_set_number

    def _unwind_undo_stack(self):
        """Rewind the undo stack to the last clean index before reload.

        The active command index is preserved so the same edits can be replayed
        after the ROM has been reopened.
        """
        self.__undo_stack_index_before_reload = self.undo_stack.index()

        index_at_last_save = self.undo_stack.cleanIndex()

        if index_at_last_save == -1:
            index_at_last_save = 0

        # unwind undo stack to get original level data
        self.undo_stack.setIndex(index_at_last_save)

    def hotswap_roms(self):
        """Reload the ROM file and restore the active editing session.

        If the open level is still attached to ROM data, Foundry captures the
        clean ROM-backed bytes first, reloads the ROM, restores ASM/FNS global
        data when those files are still present, and then reattaches the level
        plus its undoable edits.
        """
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
        """Reopen the active level from the reloaded ROM and replay edits.

        If the original level bytes cannot be found in the new ROM, the level
        is detached and the user is told to reattach it manually.
        """
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
        """Locate the pre-reload level and enemy data inside the new ROM.

        Level-object bytes are searched first, then candidate headers are
        compared after masking out jump destinations and object-set bits that
        may legitimately change during an external rebuild.

        Returns
        -------
        tuple[int, int]
            Recovered level and enemy ROM addresses, or ``(-1, -1)`` when the
            level cannot be matched.
        """
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
        """Replay the saved portion of the undo stack after reload.

        The reopened level starts from clean ROM data, so commands are replayed
        from index ``0`` until the pre-reload command position is restored.
        """
        self.undo_stack.setIndex(0)

        # reapply all the undo commands
        while self.undo_stack.canRedo() and self.undo_stack.index() < self.__undo_stack_index_before_reload:
            self.undo_stack.redo()
