"""Editable table view for world-map sprite records in Scribe.

This module owns :class:`SpriteList`, the tool-window table that mirrors the
active world's sprite collection into dropdown-backed rows. It consumes the
shared :class:`~foundry.game.level.LevelRef.LevelRef` state exposed by the tool
window, stages edits through undoable command objects, and rebuilds its rows
after drag-reorder or dropdown edits mutate the world model.

See Also
--------
scribe.gui.tool_window.table_widget : Shared table-widget behaviors and
    delegates used by Scribe tool panes.
scribe.gui.world_overview : Higher-level world editor surface that keeps the
    tool window and world view synchronized.
scribe.gui.commands : Undoable command objects used to persist sprite edits.
"""

import typing

from PySide6.QtGui import QDropEvent, QPixmap
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.gfx.objects.world_map.sprite import MAP_ITEM_SPRITES, MAP_OBJ_SPRITES
from foundry.game.level.LevelRef import LevelRef
from scribe.gui.commands import ChangeSpriteIndex, SetSpriteItem, SetSpriteType
from scribe.gui.tool_window.table_widget import (
    DialogDelegate,
    DropdownDelegate,
    TableWidget,
)
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES
from smb3parse.levels import FIRST_VALID_ROW


class SpriteList(TableWidget):
    """Show and edit the sprite list for the active world map.

    The table presents each sprite as three editable columns: sprite type, item
    type, and a read-only position summary. Column edits are translated into
    undoable commands so the world model, world view, and tool window stay in
    sync through the shared undo stack instead of mutating row widgets in
    isolation.

    In the broader editing loop, the table is the structured complement to
    dragging sprites directly in the world view. :meth:`update_content`
    projects model state into rows, :meth:`_save_sprite` turns delegate edits
    back into command objects, and :meth:`dropEvent` preserves row reordering
    through the same undo and redraw pipeline used elsewhere in Scribe.

    Parameters
    ----------
    parent
        Parent widget that owns the tool-window table.
    level_ref : LevelRef
        Shared editor reference that exposes the active world, undo stack, and
        redraw signals used by table-driven sprite edits.
    """

    def __init__(self, parent, level_ref: LevelRef):
        """Configure sprite columns, delegates, and edit hooks for the table.

        The constructor wires the table into the shared tool-window editing
        workflow. Dropdown delegates expose valid sprite and item names, the
        position column blocks direct text edits in favor of drag interactions
        in the world view, and the `cellChanged` hook routes committed edits
        into undoable sprite commands.

        Parameters
        ----------
        parent
            Parent widget that owns the sprite table.
        level_ref : LevelRef
            Shared editor reference that supplies the active world, undo stack,
            and signals inherited through :class:`TableWidget`.
        """
        super(SpriteList, self).__init__(parent, level_ref)

        self.cellChanged.connect(self._save_sprite)

        self.set_headers(["Sprite Type", "Item Type", "Map Position"])

        self.setItemDelegateForColumn(
            0,
            DropdownDelegate(self, list(MAPOBJ_NAMES.values()), list(MAP_OBJ_SPRITES.values())),
        )
        self.setItemDelegateForColumn(
            1,
            DropdownDelegate(self, list(MAPITEM_NAMES.values()), list(MAP_ITEM_SPRITES.values())),
        )
        self.setItemDelegateForColumn(
            2,
            DialogDelegate(
                self,
                "No can do",
                "You can move sprites by dragging them around in the WorldView. "
                "Make sure they are shown in the View Menu.",
            ),
        )

        self.update_content()

    def dropEvent(self, event: QDropEvent) -> None:
        """Reorder sprites after a drag-and-drop row move.

        Parameters
        ----------
        event : QDropEvent
            Drag event whose drop position identifies the destination row for
            the selected sprite.

        Notes
        -----
        The actual reorder is delegated to :class:`ChangeSpriteIndex` so the
        move participates in Scribe's undo stack and redraw lifecycle.
        """
        source_index = self.selectedIndexes()[0].row()
        target_index = self.indexAt(event.position().toPoint()).row()

        self.undo_stack.push(ChangeSpriteIndex(self.world, source_index, target_index))

        self.update_content()

    def _save_sprite(self, row: int, column: int):
        """Persist a dropdown edit for one sprite row.

        This slot turns a delegate edit back into an encoded sprite mutation on
        the shared world model. It is the table-side handoff from Qt widgets to
        Scribe's undoable command pipeline, so list edits, redraw signals, and
        later serialization all observe the same sprite-state transition.

        Parameters
        ----------
        row : int
            Row whose sprite record was changed by the user.
        column : int
            Edited column. Column ``0`` changes the sprite type and column
            ``1`` changes the item type. Column ``2`` is informational and is
            ignored.

        Notes
        -----
        The method reads the delegate-selected label back out of the cell
        widget, maps that display value to the encoded sprite or item index
        stored by the world model, and pushes the matching undoable command
        onto the shared stack.

        It also normalizes invalid Y positions before dispatching
        commands so imported or reordered sprite rows still satisfy the
        world-map row constraints expected by the renderer and serializer.
        """
        if column == 2:
            return

        sprite = self.world.sprites[row]

        widget = typing.cast(QComboBox, self.cellWidget(row, column))
        data = widget.currentText()

        if sprite.data.y < FIRST_VALID_ROW:
            sprite.data.y = FIRST_VALID_ROW

        if column == 0:
            self.undo_stack.push(SetSpriteType(sprite.data, list(MAPOBJ_NAMES.values()).index(data)))
        elif column == 1:
            self.undo_stack.push(SetSpriteItem(sprite.data, list(MAPITEM_NAMES.values()).index(data)))
        else:
            return

        self.world.data_changed.emit()

    def update_content(self):
        """Rebuild the table rows from the active world's sprite collection.

        Each row mirrors one sprite model entry into display text, icon
        previews, and a human-readable position summary. The rebuild runs after
        command-driven edits, row reordering, or external world changes so the
        tool window stays aligned with the shared world model instead of
        preserving stale cell widgets.

        Signals are blocked for the duration of the refresh so repopulating the
        rows does not recursively route display updates back into
        :meth:`_save_sprite`.
        """
        self.setRowCount(len(self.world.sprites))

        self.blockSignals(True)

        for index, sprite in enumerate(self.world.sprites):
            sprite_name = MAPOBJ_NAMES[sprite.data.type] if sprite.data.type in MAPOBJ_NAMES else str(sprite.data.type)
            sprite_type = QTableWidgetItem(sprite_name)

            if sprite.data.type in MAP_OBJ_SPRITES:
                sprite_type.setIcon(QPixmap(MAP_OBJ_SPRITES[sprite.data.type].scaled(self.iconSize())))

            item_name = MAPITEM_NAMES[sprite.data.item] if sprite.data.item in MAPITEM_NAMES else str(sprite.data.item)

            item_type = QTableWidgetItem(item_name)

            if sprite.data.item in MAP_ITEM_SPRITES:
                item_type.setIcon(QPixmap(MAP_ITEM_SPRITES[sprite.data.item].scaled(self.iconSize())))

            pos = QTableWidgetItem(f"Screen {sprite.data.screen}: x={sprite.data.x}, y={sprite.data.y}")

            self._set_map_tile_as_icon(pos, sprite.get_position())

            self.setItem(index, 0, sprite_type)
            self.setItem(index, 1, item_type)
            self.setItem(index, 2, pos)

        self.blockSignals(False)
