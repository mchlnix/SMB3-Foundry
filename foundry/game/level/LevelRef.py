"""Stable QObject proxy around the active level-like model.

This module defines :class:`LevelRef`, the indirection layer that keeps Qt
widgets, menus, and docks connected to one stable signal source while the
editor swaps between side-view levels and overworld maps. It owns the active
model reference, reconnects relay signals when that target changes, and
forwards shared operations to whichever model is loaded.

The workflow is ROM-open or level-selection action -> ``LevelRef`` target swap
-> signal reconnection -> downstream GUI surfaces receiving the same
high-level events from a new model. Maintainers working on the underlying
models should read ``Level`` and ``WorldMap`` next.

See Also
--------
foundry.game.level.Level.Level
    Side-view level model loaded through the proxy.
foundry.game.level.WorldMap.WorldMap
    Overworld model loaded through the proxy.
foundry.gui.FoundryMainWindow.FoundryMainWindow
    Main window workflow that drives model swaps through the shared reference.

Examples
--------
``LevelRef`` lets views keep one QObject connection point while the active
model changes underneath it.

>>> level_ref = LevelRef()
>>> bool(level_ref)
False
>>> level_ref.level is None
True
"""

from typing import cast

from PySide6.QtCore import QObject, Signal, SignalInstance

from foundry.game.level import EnemyItemAddress, LevelAddress
from foundry.game.level.Level import Level
from foundry.game.level.WorldMap import WorldMap
from smb3parse.constants import (
    MUSHROOM_OBJECT_SET,
    SPADE_BONUS_OBJECT_SET,
    WORLD_MAP_OBJECT_SET,
)


class LevelRef(QObject):
    """Proxy the loaded level or world map and relay its signals.

    The main window, dock widgets, and dialogs all need access to one loaded
    level-like object even though that target can switch between a normal level and an
    overworld map. ``LevelRef`` owns that indirection and re-emits the loaded
    model's change signals so the rest of the UI can stay connected to one
    stable QObject.

    Attributes
    ----------
    _internal_level : foundry.game.level.Level.Level | foundry.game.level.WorldMap.WorldMap | None
        Currently loaded level-like model, if one is active.
    data_changed : SignalInstance
        Emitted when object, enemy, or other editable data changes.
    jumps_changed : SignalInstance
        Emitted when jump definitions change.
    level_changed : SignalInstance
        Emitted when a different level-like model is loaded.
    needs_redraw : SignalInstance
        Emitted when views should repaint the loaded model.
    palette_changed : SignalInstance
        Emitted when palette-dependent rendering data changes.

    Notes
    -----
    ``LevelRef`` is the observer-friendly indirection layer for the editor:
    widgets bind to this object once, and it reconnects those bindings when the
    loaded model changes. The data flow is window action -> ``LevelRef.level``
    swap -> signal reconnection -> downstream widgets receiving the same
    high-level notifications from a new level-like target.

    See Also
    --------
    foundry.game.level.Level.Level
        Regular level model loaded through the proxy.
    foundry.game.level.WorldMap.WorldMap
        World-map model loaded through the proxy.

    Examples
    --------
    GUI code can hold onto ``LevelRef`` while the active target changes.

    >>> level_ref = LevelRef()
    >>> level_ref.fully_loaded
    False
    >>> level_ref.selected_objects
    []
    """

    needs_redraw: SignalInstance = cast(SignalInstance, Signal())
    level_changed: SignalInstance = cast(SignalInstance, Signal())
    data_changed: SignalInstance = cast(SignalInstance, Signal())
    jumps_changed: SignalInstance = cast(SignalInstance, Signal())
    palette_changed: SignalInstance = cast(SignalInstance, Signal())

    def __init__(self):
        """Initialize the level reference without an active target."""
        super(LevelRef, self).__init__()
        self._internal_level: Level | WorldMap | None = None

    def load_level(
        self,
        level_name: str,
        object_data_offset: LevelAddress,
        enemy_data_offset: EnemyItemAddress,
        object_set_number: int,
        world_number=-1,
    ):
        """Load a level-like model and reconnect the shared signals.

        This is the main handoff between ROM-opening workflows and the rest of
        the Qt UI: it chooses the correct model type, swaps ``level``, and
        emits the high-level signals that downstream widgets already observe.

        Parameters
        ----------
        level_name : str
            Display name for the level.
        object_data_offset : LevelAddress
            ROM offset for object data.
        enemy_data_offset : EnemyItemAddress
            ROM offset for enemy data.
        object_set_number : int
            Object set number that selects graphics and object definitions.
        world_number : int, optional
            One-based SMB3 world number for regular levels.
        """
        if object_set_number == WORLD_MAP_OBJECT_SET:
            self.level = WorldMap(object_data_offset)
        else:
            if object_set_number in (MUSHROOM_OBJECT_SET, SPADE_BONUS_OBJECT_SET):
                enemy_data_offset = 0x0

            self.level = Level(level_name, object_data_offset, enemy_data_offset, object_set_number, world_number)

        # actively emit, because we weren't connected yet, when the level sent it out
        self.level_changed.emit()
        self.data_changed.emit()

    @property
    def level(self):
        """Loaded level-like model.

        Most editor surfaces dereference this property instead of caching the
        active ``Level`` or ``WorldMap`` themselves, which keeps reload and
        level-swap workflows flowing through a single proxy.

        Returns
        -------
        foundry.game.level.Level.Level | foundry.game.level.WorldMap.WorldMap | None
            Loaded model, or ``None`` when nothing is open.
        """
        return self._internal_level

    @level.setter
    def level(self, level):
        """Replace the loaded model and reconnect relay signals.

        Rebinding happens here so menus, docks, and views can stay connected to
        ``LevelRef`` while the underlying model changes during ROM loads,
        world-map swaps, and undo-safe reloads.

        Parameters
        ----------
        level : foundry.game.level.Level.Level | foundry.game.level.WorldMap.WorldMap | None
            Level-like model whose signals should be re-emitted.
        """
        self._internal_level = level

        if level is None:
            return

        level.needs_redraw.connect(self.needs_redraw.emit)
        level.data_changed.connect(self.data_changed.emit)
        level.jumps_changed.connect(self.jumps_changed.emit)
        level.level_changed.connect(self.level_changed.emit)

        if hasattr(level, "palette_changed"):
            level.palette_changed.connect(self.palette_changed.emit)

    @property
    def selected_objects(self):
        """Selected objects from the loaded model.

        The property gives Qt views one shared selection source regardless of
        whether the target is a level or world map.

        Returns
        -------
        list
            Selected objects, or an empty list when no model is loaded.
        """
        if self._internal_level is None:
            return []

        return [obj for obj in self._internal_level.get_all_objects() if obj.selected]

    @selected_objects.setter
    def selected_objects(self, selected_objects):
        """Apply a new selection to the loaded model.

        Parameters
        ----------
        selected_objects : list
            Objects that should become selected.
        """
        if selected_objects == self.selected_objects:
            return

        if self._internal_level is None:
            return

        for obj in self._internal_level.get_all_objects():
            obj.selected = obj in selected_objects

        self.data_changed.emit()

    def __getattr__(self, item: str):
        """Forward unknown attributes to the loaded level-like model.

        This keeps ``LevelRef`` lightweight while still acting as the stable
        proxy object passed through the GUI, especially for callers that only
        know about the shared reference and should follow whichever model is
        active after a load or hot swap. Attribute lookup happens against the
        current target at access time so the rest of the GUI follows reloads,
        world-map swaps, and undo-safe model replacement without caching stale
        concrete objects.

        Parameters
        ----------
        item : str
            Attribute name requested by the caller.

        Returns
        -------
        object | None
            Attribute value from the loaded model, or ``None`` when unloaded.
        """
        if self._internal_level is None:
            return None
        else:
            return getattr(self._internal_level, item)

    @property
    def fully_loaded(self):
        """Report whether GUI workflows can rely on a decoded active model.

        Callers use this property to gate actions that require decoded level
        data rather than just the presence of a proxy object or pending swap,
        especially during ROM opens, closes, and hot swaps. It gives the GUI
        one readiness check that stays valid across ``Level`` and ``WorldMap``
        targets instead of reaching into the wrapped model type directly, and
        it keeps enablement logic aligned with the same truthiness contract
        used by older callers through ``__bool__``.

        Returns
        -------
        bool
            ``True`` when ``level`` resolves to a loaded model.

        Examples
        --------
        Actions can use one readiness check before touching the wrapped model.

        >>> level_ref = LevelRef()
        >>> level_ref.fully_loaded
        False
        """
        return bool(self)

    def __bool__(self):
        """Whether the proxy points at a fully loaded model.

        Truthiness mirrors ``fully_loaded`` so old boolean checks still work
        with the proxy object during load, unload, and world-map transitions
        without bypassing the proxy's loaded-state contract or reaching into the
        wrapped model directly.

        Returns
        -------
        bool
            ``True`` when the wrapped model exists and reports ``fully_loaded``.
        """
        return self._internal_level is not None and self._internal_level.fully_loaded
