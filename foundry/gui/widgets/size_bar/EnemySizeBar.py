"""Render enemy-data budget usage for the active level editor view.

This module specializes :class:`.LevelSizeBar` for SMB3 enemy and item data,
which is serialized separately from terrain objects and can be shared across
multiple levels. Maintainers typically read this file after
``foundry.gui.widgets.size_bar.LevelSizeBar`` when tracing how the editor turns
level-model byte counts into the green and orange capacity bars shown in the
status area.

See Also
--------
foundry.gui.widgets.size_bar.LevelSizeBar
    Base widget that handles the shared bar layout and label refresh flow.
foundry.gui.widgets.size_bar.size_bar.SizeBar
    Low-level bar renderer that visualizes current-versus-budget usage.
"""

from PySide6.QtGui import QColor

from foundry.game.File import ROM

from .LevelSizeBar import LevelSizeBar


class EnemySizeBar(LevelSizeBar):
    """Display enemy-data usage for the active level.

    Enemy and item data in SMB3 is stored separately from terrain objects and
    can be shared across levels, so this bar tracks a different serialized byte
    budget than :class:`LevelSizeBar`. It reuses the same presentation but
    swaps in enemy-specific size calculations and messaging.

    Parameters
    ----------
    parent : QWidget
        Parent widget that owns the size bar.
    level : LevelRef
        Level reference whose enemy usage should be displayed.
    """

    def __init__(self, parent, level):
        """Create the enemy-data size bar for a level reference.

        ``LevelSizeBar`` subscribes the widget to ``LevelRef.data_changed`` and
        builds the shared label-plus-bar surface before this constructor swaps
        in enemy-specific help text. The editor therefore keeps using the same
        refresh path after every enemy edit while exposing the separate SMB3
        enemy-data budget that can overflow into adjacent serialized enemy
        streams.

        Parameters
        ----------
        parent : QWidget
            Parent widget that owns the size bar.
        level : LevelRef
            Level reference whose enemy usage should be displayed.
        """
        super(EnemySizeBar, self).__init__(parent, level)

        self.setWhatsThis(
            "<b>Enemy Size Bar</b><br/>"
            "The enemies and items inside a level, like goombas or certain platforms, are stored as bytes in the "
            "ROM. This information is stored separately from the level objects, because multiple levels can share "
            "enemy data. Since enemy data is stored one after another, saving a level with more enemies, than "
            "it originally had, would overwrite another set of enemy data and probably cause the game to crash, if you "
            "would enter a level with broken enemy data while playing.<br/>"
            "This bar shows, how much of the available space for enemies and items is currently taken up. It will turn "
            "red, when too many enemies have been placed."
        )

    @property
    def value_color(self):
        """Return the QColor that ``LevelSizeBar.update`` assigns to enemy usage.

        Enemy edits trigger ``LevelRef.data_changed``, which causes
        :meth:`LevelSizeBar.update` to recompute the shared status surface and
        assign this color to the embedded
        :class:`~foundry.gui.widgets.size_bar.size_bar.SizeBar` before the bar
        repaints. The property therefore controls how the refresh pipeline
        renders enemy-budget usage without changing the shared widget logic
        that also serves terrain-object capacity.

        Returns
        -------
        QColor
            Orange fill color used while enemy data stays within budget.
        """
        return QColor.fromRgb(0xFFA140)

    @property
    def value_description(self):
        """Label the shared byte counter as enemy and item usage.

        :meth:`LevelSizeBar.update` inserts this text into the status label
        while it rebuilds the byte-count summary after each
        ``LevelRef.data_changed`` signal. That shared refresh path lets the
        same widget shell report different serialized budgets, and this
        override keeps the enemy-data message aligned with the separate stream
        that SMB3 stores for enemies and items.

        Returns
        -------
        str
            Description shown before the byte counts in the info label.
        """
        return "Enemies/Items"

    @property
    def current_value(self):
        """Measure the live serialized enemy stream for the active level.

        The value comes from the mutable level model rather than the last
        on-disk size, so the status bar reacts immediately while the editor is
        adding, deleting, or moving enemies and items.

        Returns
        -------
        float
            Serialized size of the active level's enemy and item data in bytes.
        """
        return self.level_ref.current_enemies_size()

    @property
    def max_value(self):
        """Compute the enemy-data budget available to the active level.

        Detached levels report an infinite budget until they are attached to a
        ROM. When managed level positions are available, the budget includes
        free space tracked for the shared enemy-data area.

        Returns
        -------
        float
            Maximum serialized enemy-data size available to the level.
        """
        enemy_size = self.level_ref.enemy_size_on_disk

        if not self.level_ref.level.attached_to_rom and enemy_size == 0:
            enemy_size = float("INF")

        elif ROM().additional_data.managed_level_positions:
            free_space_in_bank = ROM().additional_data.free_space_for_enemies()
            enemy_size += free_space_in_bank

        return enemy_size
