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
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QTableWidgetItem

from foundry.game.gfx.objects.world_map.sprite import MAP_ITEM_SPRITES, MAP_OBJ_SPRITES
from foundry.game.level.LevelRef import LevelRef
from foundry.gui.localization import tr, tr_data_name
from scribe.gui.commands import ChangeSpriteIndex, SetSpriteItem, SetSpriteType
from scribe.gui.tool_window.table_widget import (
    DialogDelegate,
    DropdownDelegate,
    TableWidget,
)
from smb3parse.constants import MAPITEM_NAMES, MAPOBJ_NAMES
from smb3parse.levels import FIRST_VALID_ROW

TR_CONTEXT = "ScribeSpriteList"


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

        self.set_headers(
            [
                tr(TR_CONTEXT, "sprite_type", "Sprite Type"),
                tr(TR_CONTEXT, "item_type", "Item Type"),
                tr(TR_CONTEXT, "map_position", "Map Position"),
            ]
        )

        self.setItemDelegateForColumn(
            0,
            DropdownDelegate(
                self,
                [tr_data_name("MapObject", name) for name in MAPOBJ_NAMES.values()],
                list(MAP_OBJ_SPRITES.values()),
                list(MAPOBJ_NAMES.keys()),
            ),
        )
        self.setItemDelegateForColumn(
            1,
            DropdownDelegate(
                self,
                [tr_data_name("MapItem", name) for name in MAPITEM_NAMES.values()],
                list(MAP_ITEM_SPRITES.values()),
                list(MAPITEM_NAMES.keys()),
            ),
        )
        self.setItemDelegateForColumn(
            2,
            self._make_position_dialog_delegate(),
        )

        self.update_content()

    def retranslate_ui(self) -> None:
        """Refresh headers and dropdown labels after a language change.

        The refresh rebuilds translated sprite and item labels while keeping
        the encoded sprite and item ids in ``Qt.UserRole`` as the command
        payload. The selected row is restored after the table rebuild so live
        language switching does not change the user's current sprite focus.
        """
        selected_row = self.selected_row
        self.set_headers(
            [
                tr(TR_CONTEXT, "sprite_type", "Sprite Type"),
                tr(TR_CONTEXT, "item_type", "Item Type"),
                tr(TR_CONTEXT, "map_position", "Map Position"),
            ]
        )
        self.setItemDelegateForColumn(
            0,
            DropdownDelegate(
                self,
                [tr_data_name("MapObject", name) for name in MAPOBJ_NAMES.values()],
                list(MAP_OBJ_SPRITES.values()),
                list(MAPOBJ_NAMES.keys()),
            ),
        )
        self.setItemDelegateForColumn(
            1,
            DropdownDelegate(
                self,
                [tr_data_name("MapItem", name) for name in MAPITEM_NAMES.values()],
                list(MAP_ITEM_SPRITES.values()),
                list(MAPITEM_NAMES.keys()),
            ),
        )
        self.setItemDelegateForColumn(2, self._make_position_dialog_delegate())
        self.update_content()
        if 0 <= selected_row < self.rowCount():
            self.selectRow(selected_row)

    def _make_position_dialog_delegate(self) -> DialogDelegate:
        """Create the read-only map-position guidance delegate.

        The delegate keeps sprite placement state owned by the world view and
        leaves this table responsible only for sprite type and item metadata.
        That boundary preserves drag-based undo replay for map movement while
        still explaining the workflow from the table cell.

        Returns
        -------
        DialogDelegate
            Informational delegate explaining that sprite position edits are
            owned by drag operations in the world view.
        """
        return DialogDelegate(
            self,
            tr(TR_CONTEXT, "no_can_do", "No can do"),
            tr(
                TR_CONTEXT,
                "help.sprite_dragging",
                "You can move sprites by dragging them around in the WorldView. Make sure they are shown in the View Menu.",
            ),
        )

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
        The method reads the delegate-selected ``Qt.UserRole`` value from the
        cell widget, not the translated label. That preserves sprite and item
        indexes as parser/world-model identity while still allowing localized
        display text in the popup editor.

        It also normalizes invalid Y positions before dispatching
        commands so imported or reordered sprite rows still satisfy the
        world-map row constraints expected by the renderer and serializer.
        """
        if column == 2:
            return

        sprite = self.world.sprites[row]

        widget = typing.cast(QComboBox, self.cellWidget(row, column))
        data = widget.currentData(Qt.ItemDataRole.UserRole)

        if sprite.data.y < FIRST_VALID_ROW:
            sprite.data.y = FIRST_VALID_ROW

        if column == 0:
            self.undo_stack.push(SetSpriteType(sprite.data, int(data)))
        elif column == 1:
            self.undo_stack.push(SetSpriteItem(sprite.data, int(data)))
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
            sprite_name = (
                tr_data_name("MapObject", MAPOBJ_NAMES[sprite.data.type])
                if sprite.data.type in MAPOBJ_NAMES
                else str(sprite.data.type)
            )
            sprite_type = QTableWidgetItem(sprite_name)
            sprite_type.setData(Qt.ItemDataRole.UserRole, sprite.data.type)

            if sprite.data.type in MAP_OBJ_SPRITES:
                sprite_type.setIcon(QPixmap(MAP_OBJ_SPRITES[sprite.data.type].scaled(self.iconSize())))

            item_name = (
                tr_data_name("MapItem", MAPITEM_NAMES[sprite.data.item])
                if sprite.data.item in MAPITEM_NAMES
                else str(sprite.data.item)
            )

            item_type = QTableWidgetItem(item_name)
            item_type.setData(Qt.ItemDataRole.UserRole, sprite.data.item)

            if sprite.data.item in MAP_ITEM_SPRITES:
                item_type.setIcon(QPixmap(MAP_ITEM_SPRITES[sprite.data.item].scaled(self.iconSize())))

            pos = QTableWidgetItem(
                tr(TR_CONTEXT, "screen_screen_x_x_y_y", "Screen {screen}: x={x}, y={y}").format(
                    screen=sprite.data.screen,
                    x=sprite.data.x,
                    y=sprite.data.y,
                )
            )

            self._set_map_tile_as_icon(pos, sprite.get_position())

            self.setItem(index, 0, sprite_type)
            self.setItem(index, 1, item_type)
            self.setItem(index, 2, pos)

        self.blockSignals(False)
