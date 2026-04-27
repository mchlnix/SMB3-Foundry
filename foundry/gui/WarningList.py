"""Popup warning surfaces for level-validation issues.

This module owns the warning popup that Foundry rebuilds from the active level
state after edits, header changes, and undoable mutations. ``WarningList``
turns ``LevelRef`` into human-readable validation messages plus the related
objects that caused each warning, while ``WarningLabel`` feeds hover events
back into the level view and object list so users can inspect the offending
data in context.

See Also
--------
foundry.game.level.LevelRef.LevelRef : Edited level state observed by the warning popup.
foundry.gui.ObjectList.ObjectList : List surface kept in sync when warnings focus objects.
foundry.gui.visualization.level.LevelView.LevelView : Canvas view that scrolls to and highlights warning targets.
"""

import json
from operator import xor
from typing import Sequence

from PySide6.QtCore import QEvent, QRect, Qt, Signal, SignalInstance
from PySide6.QtGui import QCursor, QFocusEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from foundry import data_dir
from foundry.game import GROUND
from foundry.game.gfx.objects.in_level.enemy_item import EnemyItem
from foundry.game.gfx.objects.in_level.in_level_object import InLevelObject
from foundry.game.level.LevelRef import LevelRef
from foundry.game.ObjectDefinitions import GeneratorType
from foundry.gui.dialogs.LevelHeaderEditor import CAMERA_MOVEMENTS
from foundry.gui.ObjectList import ObjectList
from foundry.gui.util import clear_layout
from foundry.gui.visualization.level.LevelView import LevelView
from smb3parse.constants import (
    DUNGEON_OBJECT_SET,
    LVL_OBJ_LEVEL_END,
    LVL_OBJ_PLAINS_DOWNWARD_VINE,
    OBJ_AUTOSCROLL,
    OBJ_BOOMBOOM,
    OBJ_CHEST_EXIT,
    OBJ_CHEST_ITEM_SETTER,
    OBJ_GOAL_CARD,
    OBJ_HAMMER_BRO,
    OBJ_PIPE_EXITS,
    OBJ_TREASURE_CHEST,
)


class WarningList(QWidget):
    """Popup list of level validation warnings.

    The widget derives warnings from the active level model, including SMB3
    crash-prone object placements, jump/header mismatches, autoscroll setup,
    incompatible enemy groups, and chest/goal-card conventions. Hovering a
    warning selects and scrolls to the related objects. It acts as Foundry's
    live lint pass for ROM-editing mistakes that are legal to encode but risky
    to ship: impossible placements, engine quirks, object-set rules, and
    crash-prone combinations discovered through SMB3-specific editor history.
    The workflow is deliberately reactive: ``LevelRef.data_changed`` triggers a
    warning recomputation, the popup rebuilds its warning-label widgets from the
    resulting text/object pairs, and hovering a label pushes the related
    selection back into the level view and object list so the user can inspect
    the offending data in context.

    Parameters
    ----------
    parent : QWidget
        Parent Qt widget that owns this object.
    level_ref : LevelRef
        Reference to the edited level.
    level_view_ref : LevelView
        Reference to the level view used by the warning list.
    object_list_ref : ObjectList
        Reference to the object list used by the warning list.

    Attributes
    ----------
    _enemy_dict : dict[str, tuple[str, str]]
        Enemy-name lookup mapping to incompatibility clan and group.
    level_ref : LevelRef
        Reference that owns the edited level data.
    level_view_ref : LevelView
        Level view used to select and scroll to warning-related objects.
    object_list : ObjectList
        Object list kept in sync when warning hovers change selection.
    warnings : list[tuple[str, list[InLevelObject]]]
        Current warning text paired with the related in-level objects.
    warnings_updated : SignalInstance
        Signal emitted whenever the warning list becomes empty or non-empty.
    """

    warnings_updated: SignalInstance = Signal(bool)

    def __init__(
        self,
        parent,
        level_ref: LevelRef,
        level_view_ref: LevelView,
        object_list_ref: ObjectList,
    ):
        """Create the warning popup and enemy compatibility lookup.

        Construction wires warning recomputation to level changes, builds the
        enemy-clan lookup table, and prepares the popup/list synchronization
        state used by hover-to-focus behavior.

        Parameters
        ----------
        parent : QWidget
            Parent Qt widget that owns this object.
        level_ref : LevelRef
            Reference to the edited level.
        level_view_ref : LevelView
            Reference to the level view used by the warning list.
        object_list_ref : ObjectList
            Reference to the object list used by the warning list.
        """
        super(WarningList, self).__init__(parent)

        self.level_ref = level_ref
        self.level_ref.data_changed.connect(self._update_warnings)

        self.level_view_ref = level_view_ref
        self.object_list = object_list_ref

        self.setLayout(QVBoxLayout())
        self.setWindowFlag(Qt.WindowType.Popup)
        self.layout().setContentsMargins(5, 5, 5, 5)

        self._enemy_dict: dict[str, tuple[str, str]] = {}
        self._build_enemy_clan_dict()

        self.warnings: list[tuple[str, list[InLevelObject]]] = []

    def _update_warnings(self):
        """Recompute warnings from the active level state.

        This method keeps warning generation close to the level data it checks:
        bounds, jump destinations, generator edge cases, autoscroll rows,
        enemy compatibility, Boom Boom placement, pipe exits, chest exits, and
        goal-card requirements. The resulting warnings drive both the popup
        contents and the hover-to-select workflow used to jump from a warning
        back to the offending objects in the level view.
        """
        self.warnings.clear()

        level = self.level_ref.level

        # all jump objects should be inside the level
        for jump in level.jumps:
            if not level.get_rect(1).contains(jump.get_rect(1, level.is_vertical)):
                self.warn(f"{jump} is outside of the level bounds.", [])

        # a jump should not be set without a next area also set
        if level.jumps and not level.has_next_area:
            self.warn("Level has jumps set, but no Jump Destination in Level Header.", [])

        # level objects and enemies should be inside the level
        for obj in level.get_all_objects():
            if isinstance(obj, EnemyItem) and obj.obj_index == OBJ_AUTOSCROLL:
                continue

            if not level.get_rect().contains(obj.get_rect()):
                self.warn(f"{obj} is outside of level bounds.", [obj])

        # level objects that expand to the ground should not hit the level edge
        for obj in level.objects:
            if obj.object_info == LVL_OBJ_PLAINS_DOWNWARD_VINE:
                continue

            if obj.generator_type in [
                GeneratorType.HORIZ_TO_GROUND,
                GeneratorType.PYRAMID_TO_GROUND,
            ]:
                if obj.y_position + obj.rendered_height == GROUND:
                    self.warn(
                        f"{obj} extends until the level bottom. This can crash the game.",
                        [obj],
                    )

        # objects that expand to the ground cannot be in vertical levels
        objects_that_extend_to_ground = [
            obj
            for obj in level.objects
            if obj.generator_type in (GeneratorType.HORIZ_TO_GROUND, GeneratorType.PYRAMID_TO_GROUND)
            and obj.object_info != LVL_OBJ_PLAINS_DOWNWARD_VINE
        ]

        if level.is_vertical and objects_that_extend_to_ground:
            self.warn(
                "You have objects that extend to the ground in a vertical level. This might crash the game.",
                objects_that_extend_to_ground,
            )

        # autoscroll objects
        for item in level.enemies:
            if item.obj_index == OBJ_AUTOSCROLL:
                if item.y_position >= 0x60:
                    self.warn(
                        f"{item}'s y-position is too low. Maximum is 95 or 0x5F.",
                        [item],
                    )

                if level.header.scroll_type_index != 0:
                    self.warn(
                        f"Level has auto scrolling enabled, but the scrolling type in the level header is not "
                        f"'{CAMERA_MOVEMENTS[0]}. This might not work as expected.",
                        [],
                    )

        autoscroll_items = [item for item in level.enemies if item.obj_index == OBJ_AUTOSCROLL]

        if len(autoscroll_items) > 1:
            self.warn(
                "Level has more than one AutoScrolling items. Does that work?",
                autoscroll_items,
            )

        # no items that would crash the game
        for obj in level.objects:
            if obj.name == "MSG_CRASH" or "SMAS only" in obj.name:
                self.warn(
                    f"Object at {obj.get_rendered_position()} will likely cause the game to crash, when loading "
                    "or on screen.",
                    [obj],
                )

        # incompatible enemies
        enemies_in_level = [enemy for enemy in level.enemies if enemy.name in self._enemy_dict]

        for enemy in enemies_in_level.copy():
            enemies_in_level.pop(0)

            clan, group = self._enemy_dict[enemy.name]

            for other_enemy in enemies_in_level:
                other_clan, other_group = self._enemy_dict[other_enemy.name]

                if clan == other_clan and group != other_group:
                    self.warn(
                        f"'{enemy}' incompatible with '{other_enemy}', when on same screen",
                        [enemy, other_enemy],
                    )

        # boom boom not in dungeon level
        for enemy in level.enemies:
            if enemy.type != OBJ_BOOMBOOM:
                continue

            if level.object_set_number != DUNGEON_OBJECT_SET:
                self.warn(
                    "You should only use 'BoomBoom' enemies in levels of object set 'Dungeon'.",
                    [enemy],
                )

            if enemy.y_position < 0x10:
                self.warn(
                    "If your 'BoomBoom' has a lower y-position than 16, you need to add 1 to your Lock Index.",
                    [enemy],
                )

            break

        for enemy in level.enemies:
            if enemy.type != OBJ_PIPE_EXITS:
                continue

            if not level.header.pipe_ends_level:
                self.warn(
                    "You have a Pipe Pair Exit set (Level Settings), " "but Pipes don't end your Level (Level Header).",
                    [],
                )

            break

        chest_exit_objects = self._find_enemies_in_level(OBJ_CHEST_EXIT)
        chest_exit_items = self._find_enemies_in_level(OBJ_CHEST_ITEM_SETTER)
        chest_objects = self._find_enemies_in_level(OBJ_TREASURE_CHEST)
        hammer_bro_objects = self._find_enemies_in_level(OBJ_HAMMER_BRO)

        # hammer bro level does not end with collecting the chest
        if hammer_bro_objects and not chest_exit_objects:
            self.warn(
                "You have a Hammer Bro in your level, but it does not end by getting the chest. "
                "Go to Level Settings.",
                hammer_bro_objects,
            )

        # level ends with chest, but no item set
        if not hammer_bro_objects and not chest_exit_items and chest_exit_objects:
            self.warn(
                "You've set the level to end with getting a Chest, but there is no item in the chest.",
                chest_exit_objects,
            )

        if hammer_bro_objects and chest_exit_items:
            self.warn(
                "You are setting the item of a chest, but in Hammer Bros Levels, this is done through the Hammer "
                "Bros of the world map.",
                chest_exit_items,
            )

        if chest_exit_items and not chest_objects:
            self.warn(
                f"You have {len(chest_exit_items)} Chest Item objects, but no chest in the level to set items for.",
                chest_exit_items,
            )
        elif chest_objects and not chest_exit_items:
            self.warn(
                f"You have {len(chest_objects)} Chests, but no object that sets their items in the level. ",
                chest_objects,
            )

        if xor(self._is_object_in_level(*LVL_OBJ_LEVEL_END), any(self._find_enemies_in_level(OBJ_GOAL_CARD))):
            self.warn("You shouldn't have a level ending object without a goal card item, but you can have neither.")

        self.update()
        self.warnings_updated.emit(bool(self.warnings))

    def _find_enemies_in_level(self, enemy_id: int) -> list[EnemyItem]:
        """Filter the level's enemy stream to one SMB3 enemy or item id.

        Several warnings reason about incompatible enemy combinations, so they
        need a filtered view of the level's stored enemy/item stream rather
        than the full mixed editor selection state.
        This keeps the warning rules declarative while they rebuild the popup
        after level edits.

        Parameters
        ----------
        enemy_id : int
            Identifier of the enemy.

        Returns
        -------
        list[EnemyItem]
            Matching enemies/items in the edited level.
        """
        return [enemy for enemy in self.level_ref.level.enemies if enemy.type == enemy_id]

    def _is_object_in_level(self, domain: int, object_index: int) -> bool:
        """Check for an SMB3 level object while recomputing warning rules.

        ``_update_warnings`` calls this helper when one warning rule needs to
        know whether a specific SMB3 object combination exists in the edited
        level. The helper answers that one predicate in domain/id terms instead
        of making every rule rescan ``level.objects`` itself. A false result
        stops that warning branch with no popup entry. A true result lets the
        same recomputation add a warning row, and that row later becomes a
        hover-focus target in the warning list. The method therefore sits in
        the middle of the edit-to-warning pipeline: object edits change level
        state, ``_update_warnings`` re-evaluates each rule, this helper answers
        one object-presence predicate, and the resulting warning row becomes
        focusable UI state for the user.

        Parameters
        ----------
        domain : int
            Object domain that determines how the object is interpreted.
        object_index : int
            Index of the object.

        Returns
        -------
        bool
            ``True`` when an object has the queried domain and id.
        """
        return any(
            [
                lvl_obj
                for lvl_obj in self.level_ref.level.objects
                if lvl_obj.domain == domain and lvl_obj.obj_index == object_index
            ]
        )

    def _build_enemy_clan_dict(self):
        """Load enemy incompatibility groups from bundled JSON data."""
        with (data_dir / "enemy_data.json").open("r") as enemy_data_file:
            enemy_data = json.loads(enemy_data_file.read())

            self._enemy_dict.clear()

            for clan, groups in enemy_data.items():
                for group, enemy_list in groups.items():
                    for enemy in enemy_list:
                        self._enemy_dict[enemy] = (clan, group)

    def warn(self, msg: str, objects: Sequence[InLevelObject] | None = None):
        """Append a warning and optional related objects.

        The method stores the warning payload for later popup rebuilds and
        preserves the object references needed by hover-to-select behavior.

        Parameters
        ----------
        msg : str
            Warning text to display.
        objects : Sequence[InLevelObject] | None, optional
            Objects selected when the warning label is hovered.
        """
        if objects is None:
            objects = []

        self.warnings.append((msg, list(objects)))

    def update(self):
        """Rebuild warning labels from the active warning list."""
        self.hide()

        clear_layout(self.layout())

        for warning in self.warnings:
            warning_message, related_objects = warning

            label = WarningLabel(warning_message, related_objects)
            label.hovered.connect(self._focus_objects)

            self.layout().addWidget(label)

        super(WarningList, self).update()

    def show(self):
        """Show the popup just below the cursor."""
        pos = QCursor.pos()
        pos.setY(pos.y() + 10)

        self.setGeometry(QRect(pos, self.layout().sizeHint()))

        super(WarningList, self).show()

    def _focus_objects(self):
        """Select and scroll to objects related to a hovered warning."""
        sender_widget = self.sender()

        assert isinstance(sender_widget, WarningLabel)
        objects = sender_widget.related_objects

        if objects:
            self.level_ref.blockSignals(True)

            self.level_view_ref.select_objects(objects)
            self.level_view_ref.scroll_to_objects(objects)
            self.object_list.update_content()

            self.level_ref.blockSignals(False)

    def focusOutEvent(self, event: QFocusEvent):
        """Hide the popup when focus leaves it.

        Parameters
        ----------
        event : QFocusEvent
            Qt event delivered to the widget.
        """
        self.hide()

        super(WarningList, self).focusOutEvent(event)


class WarningLabel(QLabel):
    """Represent one warning as a hoverable jump target back into the editor.

    ``WarningList`` stores warnings as text plus related objects, but the popup
    itself needs a widget that can participate in Qt layout and mouse events.
    This label is that adapter: it renders the warning text, remembers the
    related in-level objects, and emits ``hovered`` so the popup can drive the
    editor selection, scroll position, and object-list focus from a simple
    mouse-over gesture. That makes each row more than static text: it is a
    lightweight controller for the warning-review workflow, where hovering a
    lint finding immediately answers "which object is this talking about?" in
    the live level editor.

    Parameters
    ----------
    text : str
        Warning text to display.
    related_objects : list[InLevelObject]
        Objects associated with the warning.

    Attributes
    ----------
    hovered : SignalInstance
        Signal emitted when the cursor enters the label so the popup can
        synchronize editor selection.
    related_objects : list[InLevelObject]
        Objects associated with the warning row.

    See Also
    --------
    WarningList
        Creates these labels and uses their hover events to focus warnings in
        the live editor.
    """

    hovered: SignalInstance = Signal()

    def __init__(self, text: str, related_objects: list[InLevelObject]):
        """Create a warning row tied to specific level objects.

        ``WarningList`` creates one label per warning and reconnects its hover
        signal so entering the row can focus the matching objects in the live
        level view. The label therefore carries both the rendered warning text
        and the object references that drive the popup's hover-to-select flow
        back into the editor. Once stored here, those references are what
        ``enterEvent`` hands back to the popup so the warning row can retarget
        selection, scrolling, and object-list focus without recomputing the
        warning. Initialization is therefore the point where a passive warning
        message becomes an interactive editor target: the popup creates the
        row, stores its related objects, and later hover events use that stored
        state to drive editor focus.

        Parameters
        ----------
        text : str
            Warning text to display.
        related_objects : list[InLevelObject]
            Objects associated with the warning.
        """
        super(WarningLabel, self).__init__(text)

        self.related_objects = related_objects

    def enterEvent(self, event: QEvent):
        """Emit ``hovered`` before delegating the enter event.

        Hover is the bridge between the popup list and the editor canvas: the
        signal tells ``WarningList`` to select and scroll the related objects
        before Qt handles the visual hover state.

        Parameters
        ----------
        event : QEvent
            Qt event delivered to the widget.

        Returns
        -------
        QEvent | None
            Result returned by the base Qt handler, if any.
        """
        self.hovered.emit()

        return super(WarningLabel, self).enterEvent(event)
