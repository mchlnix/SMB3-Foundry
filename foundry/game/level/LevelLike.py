"""Shared level-like contract for Foundry's ROM-backed editor models.

This module defines :class:`LevelLike`, the abstract bridge that lets generic
editor code work with both side-view levels and world maps through one shared
surface for drawing, hit testing, sizing, and object lookup. It sits between
concrete SMB3 decode models and higher-level views, lists, and undo helpers
that should not branch on the exact model type.

The workflow is concrete model -> ``LevelLike`` contract -> shared editor
tools. Maintainers who need the concrete behavior should read
``foundry.game.level.Level`` and ``foundry.game.level.WorldMap`` next.

See Also
--------
foundry.game.level.Level.Level
    Concrete side-view implementation of the shared contract.
foundry.game.level.WorldMap.WorldMap
    Concrete overworld implementation of the shared contract.
foundry.game.level.LevelRef.LevelRef
    Stable proxy that forwards GUI work to the active level-like model.

Examples
--------
Shared editor code can rely on the common contract without branching on the
loaded model type.

>>> model = level_ref.level
>>> model.object_at(4, 6)
>>> len(model.get_all_objects()) >= 0
True
"""

import abc

from foundry.game.ObjectSet import ObjectSet
from smb3parse.levels import LevelBase


class LevelLike(LevelBase, abc.ABC):
    """Define the common editor contract for levels and world maps.

    ``Level`` and ``WorldMap`` expose different underlying SMB3 data, but the
    editor still needs a shared surface for drawing, indexing, selection, and
    object lookup. This abstract base class captures that contract on top of
    ``smb3parse``'s ``LevelBase``.

    The data flow is concrete ROM-backed model -> ``LevelLike`` interface ->
    generic editor code that can ask for objects, drawing, and lookup services
    without branching on level type.

    Parameters
    ----------
    object_set : ObjectSet
        Object set that controls tiles, graphics, or level object behavior.
    layout_address : int
        ROM address of the level or world map layout data.

    See Also
    --------
    foundry.game.level.Level.Level
        Side-view implementation of this contract.
    foundry.game.level.WorldMap.WorldMap
        Overworld implementation of this contract.

    Examples
    --------
    Generic editor helpers can size and query the active model without
    branching on its concrete type.

    >>> model = level_ref.level
    >>> bounds = (model.width, model.height)
    >>> isinstance(bounds[0], int) and isinstance(bounds[1], int)
    True
    """

    def __init__(self, object_set: ObjectSet, layout_address):
        """Anchor the shared editor contract to one ROM-backed layout.

        Concrete subclasses decode different SMB3 data, but they all start
        from the same two pieces of identity: which object set defines their
        rendering or behavior and which ROM address anchors their layout data.
        Shared editor code depends on that common identity remaining stable
        while subclasses build their own decoded object collections, draw
        caches, or ROM-writing state on top of it.

        Parameters
        ----------
        object_set : ObjectSet
            Object set that controls tiles, graphics, or level object behavior.
        layout_address : int
            ROM address of the level or world map layout data.
        """
        super(LevelLike, self).__init__(object_set, layout_address)

    @abc.abstractmethod
    def index_of(self, obj):
        """Translate one editor object into the model's storage ordering.

        Concrete subclasses use this to translate a selected model object back
        into the order expected by undo commands, lists, and ROM-writing code.

        Parameters
        ----------
        obj : object
            Editor object whose index should be returned.
        """
        pass

    @abc.abstractmethod
    def object_at(self, x, y):
        """Resolve a grid-space hit test into the active editor object.

        Views use this hit-test hook to map widget clicks back into model
        objects without branching on whether they are editing a level or a
        world map.

        Parameters
        ----------
        x : int
            Horizontal grid coordinate.
        y : int
            Vertical grid coordinate.
        """
        pass

    @abc.abstractmethod
    def get_all_objects(self):
        """Expose the full selectable object stream for shared editor tools.

        Generic selection and list code relies on this shared hook instead of
        knowing whether the subclass stores tiles, level objects, enemies, or
        world-map objects.
        """
        pass

    @abc.abstractmethod
    def draw(self, dc, block_length, transparency, show_expansion):
        """Draw the model through the legacy level-like interface.

        Foundry's newer Qt views mostly delegate drawing to dedicated drawer
        classes, but some code still expects level-like models to offer this
        rendering hook. Concrete subclasses therefore use this method as the
        adapter from decoded ROM-backed state into older paint paths that still
        ask the model itself to render.

        Parameters
        ----------
        dc : object
            Painter or drawing context supplied by the caller.
        block_length : int
            Rendered block size in pixels.
        transparency : bool
            Whether semi-transparent drawing should be used when supported.
        show_expansion : bool
            Whether expansion overlays should be shown when supported.
        """
        pass

    @property
    def width(self) -> int:
        """Report the horizontal grid span that shared editor code should use.

        Concrete subclasses provide this so generic views and selection logic
        can size widgets without knowing whether they are editing a level or a
        world map. Keeping the width on the shared contract lets layout,
        viewport, and hit-test code derive consistent horizontal bounds from
        whichever model is currently active, so the same view code can size
        scroll regions, selection bounds, and paint surfaces before it knows
        which concrete level-like implementation is loaded. In practice this is
        the horizontal dimension that flows from decoded ROM layout state into
        shared scene sizing, scroll-range setup, and rectangular selection
        bounds across every level-like workflow.

        Raises
        ------
        NotImplementedError
            Always raised by the abstract base implementation.

        Examples
        --------
        Generic sizing code can treat levels and world maps the same way.

        >>> model = level_ref.level
        >>> model.width >= 0
        True
        """
        raise NotImplementedError()

    @property
    def height(self) -> int:
        """Expose the vertical grid span required by shared editor code.

        Concrete subclasses provide this so generic views and selection logic
        can size widgets without knowing whether they are editing a level or a
        world map. Layout and redraw code use this together with ``width`` to
        preserve one sizing contract across level and overworld workflows.

        Raises
        ------
        NotImplementedError
            Always raised by the abstract base implementation.
        """
        raise NotImplementedError()
