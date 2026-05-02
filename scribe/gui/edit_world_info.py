"""Edit world-level metadata and reorganization settings in Scribe.

This module provides :class:`EditWorldInfo`, the dialog that lets Scribe
maintainers adjust per-world metadata such as palette, music, animation timing,
bottom-border tile, and map-scroll behavior while also staging world-overview
reorganization changes. The dialog combines immediate preview updates on the
active :class:`~foundry.game.level.WorldMap.WorldMap` with deferred
``QUndoStack`` commands so the user can inspect the result before the final
world-info transaction is committed.

The widget builds its editing surface around
:class:`scribe.gui.world_overview.WorldOverview`, which validates aggregate
screen and level-pointer counts before the dialog can close. Readers who need
to follow the commit path after this dialog closes should inspect
``scribe.gui.commands`` for the undo commands and
``scribe.gui.world_overview`` for the cross-world staging model.

See Also
--------
scribe.gui.world_overview.WorldOverview
    Collects cross-world screen-count and level-count edits that this dialog
    validates and finalizes.
scribe.gui.commands
    Defines the undo commands pushed by the dialog when metadata changes are
    committed.
"""

from typing import cast

from PySide6.QtCore import QSize
from PySide6.QtGui import QCloseEvent, QPainter, QPixmap, Qt, QUndoStack
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from foundry.game.File import ROM
from foundry.game.gfx.block_cache import get_worldmap_tile
from foundry.game.level.LevelRef import LevelRef
from foundry.game.level.WorldMap import WorldMap
from foundry.gui import label_and_widget
from foundry.gui.dialogs.CustomDialog import CustomDialog
from foundry.gui.localization import tr, tr_data_name
from foundry.gui.widgets.Spinner import Spinner
from foundry.gui.windows.BlockViewer import BlockBank
from scribe.gui.commands import (
    SetWorldScroll,
    WorldBottomTile,
    WorldMusicIndex,
    WorldPaletteIndex,
    WorldTickPerFrame,
)
from scribe.gui.world_overview import WorldOverview
from smb3parse.constants import MUSIC_THEMES
from smb3parse.levels import NO_MAP_SCROLLING, WORLD_MAP_PALETTE_COUNT

TR_CONTEXT = "ScribeEditWorldInfo"


class EditWorldInfo(CustomDialog):
    """Edit one world's metadata and staged reorganization changes.

    The dialog owns the short-lived UI state for one editing session. It keeps
    visual previews responsive while the user tweaks palette-dependent fields,
    then consolidates the accepted metadata and world-overview edits into the
    shared undo history when the dialog closes successfully.

    Parameters
    ----------
    parent : QWidget
        Owning widget whose parent chain exposes the shared ``QUndoStack``
        used by Scribe editing dialogs.
    world_map : WorldMap
        The active world map whose metadata is previewed, validated, and
        ultimately committed through undo commands.

    Attributes
    ----------
    world_map : WorldMap
        World map being edited by the dialog.
    orig_tick_per_frame : int
        Original animation tick count captured so the dialog can preview direct
        edits immediately and still commit them as one undoable command on
        close.
    world_overview : WorldOverview
        Table widget that stages cross-world screen-count and level-count
        changes and reports whether the overall arrangement is valid.
    scrolls_check_box : QCheckBox
        Toggle that maps the world's scroll flag between SMB3's scrolling and
        non-scrolling encodings.
    palette_layout : QLayout
        Label/control row for the palette spinner; live retranslation owns the
        label while the spinner retains the encoded palette value.
    music_dropdown : QComboBox
        Dropdown that displays localized music names while storing the stable
        SMB3 music index as item data.
    music_layout : QLayout
        Label/control row for the music selector, refreshed without changing
        the selected music index.
    bottom_border_layout : QLayout
        Label/control row for the bottom-border tile preview button.
    world_data_group : QGroupBox
        Container for per-world metadata controls separate from the staged
        world-overview table.
    icon_button : QPushButton
        Button that previews and launches selection of the world's bottom
        border tile.
    ticks_per_frame_layout : QLayout
        Label/control row for animation timing. The spinner previews direct
        world-data changes until close commits them through the undo stack.
    animation_hint_label : QLabel
        Label for world-specific scrolling and animation constraints.
    error_label : QLabel
        Validation summary sourced from ``world_overview.status_msg``.
    ok_button : QPushButton
        Close button that stays disabled while staged world-overview edits are
        invalid.

    Notes
    -----
    Palette and animation changes are previewed immediately on ``world_map`` so
    the embedded overview stays visually current while the dialog is open.
    ``closeEvent`` restores the original tick count before pushing
    :class:`~scribe.gui.commands.WorldTickPerFrame`, keeping the final change in
    the shared undo history rather than baking in an untracked mutation.
    """

    def __init__(self, parent: QWidget, world_map: WorldMap):
        """Build the world-info editor for one world map.

        The constructor stages one editing session around two data paths that
        stay separate until :meth:`closeEvent` commits the result. Metadata
        controls for scrolling, palette, music, bottom-border tile, and frame
        timing are connected first so palette- and animation-sensitive changes
        can repaint the live :attr:`world_map` preview immediately while the
        dialog stays open. The method then snapshots
        :attr:`orig_tick_per_frame`, because frame timing is previewed through a
        direct mutation that must be restored and replayed later as
        :class:`~scribe.gui.commands.WorldTickPerFrame`.

        After the per-world controls are in place, the constructor wraps the
        same world in a temporary :class:`~foundry.game.level.LevelRef.LevelRef`
        and gives it to :class:`WorldOverview`. That table owns the
        cross-world reorganization path: it stages screen-count and
        level-pointer redistribution, emits validation changes back into this
        dialog, and blocks closing until the proposed layout is internally
        consistent. The remaining labels and the OK button mirror that staged
        state so the user can see whether the world-overview edits are ready to
        finalize before any undo commands are pushed.

        Parameters
        ----------
        parent : QWidget
            Owning widget whose parent chain is expected to provide the shared
            ``QUndoStack``.
        world_map : WorldMap
            World map whose metadata and world-layout relationships are edited
            by this dialog.
        """
        super(EditWorldInfo, self).__init__(parent, tr(TR_CONTEXT, "edit_world_info", "Edit World Info"))

        self.world_map = world_map

        self.setLayout(QVBoxLayout())

        # world data
        layout = QVBoxLayout()

        self.scrolls_check_box = QCheckBox()
        self.scrolls_check_box.setChecked(self.world_map.data.map_scroll not in [0, NO_MAP_SCROLLING])

        layout.addWidget(self.scrolls_check_box)

        palette_spin_box = Spinner(self, maximum=WORLD_MAP_PALETTE_COUNT - 1)
        palette_spin_box.setValue(self.world_map.data.palette_index)
        palette_spin_box.valueChanged.connect(self._change_palette_index)

        self.palette_layout = label_and_widget("", palette_spin_box)
        layout.addLayout(self.palette_layout)

        self.music_dropdown = QComboBox(self)
        for value, name in MUSIC_THEMES.items():
            self.music_dropdown.addItem(f"{tr_data_name('MusicTheme', name)} ({value:#x})", value)
        self.music_dropdown.currentIndexChanged.connect(self._change_music_index)
        self.music_dropdown.setCurrentIndex(max(0, self.music_dropdown.findData(world_map.data.music_index)))

        self.music_layout = label_and_widget("", self.music_dropdown)
        layout.addLayout(self.music_layout)

        self.icon_button = QPushButton("")
        self.icon_button.clicked.connect(self._on_button_press)
        self._update_button_icon()

        self.bottom_border_layout = label_and_widget("", self.icon_button)
        layout.addLayout(self.bottom_border_layout)

        self.world_data_group = QGroupBox()
        self.world_data_group.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.world_data_group.setLayout(layout)

        self.orig_tick_per_frame = self.world_map.data.frame_tick_count

        ticks_per_frame_spin_box = Spinner(self, maximum=0xFF, base=10)
        ticks_per_frame_spin_box.setValue(self.world_map.data.frame_tick_count)
        ticks_per_frame_spin_box.valueChanged.connect(self._change_anim_frame)

        self.ticks_per_frame_layout = label_and_widget("", ticks_per_frame_spin_box)
        layout.addLayout(self.ticks_per_frame_layout)

        self.animation_hint_label = QLabel()
        layout.addWidget(self.animation_hint_label)

        self.layout().addWidget(self.world_data_group)

        level_ref = LevelRef()
        level_ref.level = self.world_map

        self.world_overview = WorldOverview(self, level_ref, ROM())
        self.world_overview.data_changed.connect(self._update_hint_labels)
        self.world_overview.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.layout().addWidget(self.world_overview)

        self.error_label = QLabel(self.world_overview.status_msg)
        self.layout().addWidget(self.error_label)

        # ok button
        self.ok_button = QPushButton(tr("Common", "ok", "OK"))
        self.ok_button.clicked.connect(self.close)

        self.layout().addWidget(self.ok_button)

        self.retranslate_ui()

    @property
    def undo_stack(self) -> QUndoStack:
        """Access the main undo stack used for world-info commits.

        The dialog does not own its own command history. Instead it resolves
        the parent editor's named stack on demand so metadata changes and world
        reorganization commands join the same undo timeline as other Scribe
        edits.

        Returns
        -------
        QUndoStack
            Stack named ``"undo_stack"`` found through the window's parent
            hierarchy.
        """
        return cast(QUndoStack, self.window().parent().findChild(QUndoStack, "undo_stack"))

    def _update_button_icon(self):
        """Refresh the bottom-border tile preview button.

        The preview is rendered from the selected bottom-border tile index and
        palette selection so the button mirrors the state that would be written
        by :class:`~scribe.gui.commands.WorldBottomTile` and
        :class:`~scribe.gui.commands.WorldPaletteIndex`.
        """
        block = get_worldmap_tile(self.world_map.data.bottom_border_tile, self.world_map.data.palette_index)

        block_icon = QPixmap(QSize(32, 32))

        painter = QPainter(block_icon)
        block.draw(painter, 0, 0, 32)
        painter.end()

        self.icon_button.setIcon(block_icon)

    def _update_hint_labels(self):
        """Update validation and world-specific hint labels.

        Notes
        -----
        The dialog warns about worlds with special scrolling or animation
        behavior and mirrors :meth:`scribe.gui.world_overview.WorldOverview.valid`
        so invalid aggregate world layouts cannot be committed.
        """
        world_number = self.world_map.data.index

        if world_number == 4:
            self.animation_hint_label.setText(
                tr(TR_CONTEXT, "note.world_5_scroll_limit", "Note: World 5 cannot scroll and isn't animated")
            )
        elif world_number == 7:
            self.animation_hint_label.setText(
                tr(
                    TR_CONTEXT,
                    "note.world_8_scroll_limit",
                    "Note: World 8 cannot scroll and the last screen isn't animated",
                )
            )
        else:
            self.animation_hint_label.setText("")

        self.error_label.setText(self.world_overview.status_msg)

        if self.world_overview.valid():
            self.error_label.setStyleSheet("QLabel { }")
        else:
            self.error_label.setStyleSheet("QLabel { color : red; }")

        self.ok_button.setEnabled(self.world_overview.valid())

    def retranslate_ui(self) -> None:
        """Refresh all visible world-info labels after a language change.

        The method owns the live-translation workflow for this dialog: the
        title, group title, form labels, music choices, validation hints, child
        overview widget, footer text, and OK button are rewritten from catalogs
        while encoded combo-box data and staged world edits remain unchanged.
        It preserves the dialog's edit state and uses the normal hint-label
        path as a display boundary so validation text and world-specific notes
        stay in the active language without committing metadata changes.
        """
        self.setWindowTitle(tr(TR_CONTEXT, "edit_world_info", "Edit World Info"))
        self.world_data_group.setTitle(tr(TR_CONTEXT, "world_data", "World Data"))
        self.scrolls_check_box.setText(
            tr(TR_CONTEXT, "label.edge_scroll_enabled", "Scrolls to next screen, when at the edge")
        )
        self._set_layout_label_text(self.palette_layout, tr(TR_CONTEXT, "color_palette_index", "Color Palette Index"))
        self._set_layout_label_text(self.music_layout, tr(TR_CONTEXT, "music_theme", "Music Theme"))
        self._set_layout_label_text(
            self.bottom_border_layout, tr(TR_CONTEXT, "bottom_border_tile", "Bottom Border Tile")
        )
        self._set_layout_label_text(
            self.ticks_per_frame_layout,
            tr(TR_CONTEXT, "ticks_between_animation_frames", "Ticks between Animation Frames"),
        )
        current_music_index = self.music_dropdown.currentData()
        self.music_dropdown.blockSignals(True)
        for index in range(self.music_dropdown.count()):
            music_index = self.music_dropdown.itemData(index)
            music_name = MUSIC_THEMES[music_index]
            self.music_dropdown.setItemText(index, f"{tr_data_name('MusicTheme', music_name)} ({music_index:#x})")
        self.music_dropdown.setCurrentIndex(max(0, self.music_dropdown.findData(current_music_index)))
        self.music_dropdown.blockSignals(False)
        self.world_overview.retranslate_ui()
        self.ok_button.setText(tr("Common", "ok", "OK"))
        self._update_hint_labels()

    @staticmethod
    def _set_layout_label_text(layout, text: str) -> None:
        """Update the label created by ``label_and_widget``.

        The helper is the small display boundary used by live retranslation for
        row layouts that pair a translated label with a stateful editor widget.
        Only the label text is replaced; palette, music, tile, and timing
        widget state remains owned by the dialog controls.

        Parameters
        ----------
        layout
            Two-item row layout returned by :func:`foundry.gui.label_and_widget`.
        text : str
            Catalog-backed label text to apply to the row's first widget.

        """
        label = layout.itemAt(0).widget()
        if isinstance(label, QLabel):
            label.setText(text)

    def _on_button_press(self):
        """Open the block picker for the bottom-border tile.

        Notes
        -----
        The temporary :class:`BlockBank` is used only as a chooser. Once the
        user picks a tile, the callback hides the picker, pushes
        :class:`~scribe.gui.commands.WorldBottomTile` to the shared undo stack,
        and redraws the preview icon from the updated world state. The chooser
        never owns persistent bottom-border state.
        """
        block_bank = BlockBank(None, palette_group_index=self.world_map.data.palette_index)
        block_bank.setWindowModality(Qt.WindowModal)

        block_bank.last_clicked_index = self.world_map.data.bottom_border_tile

        def _callback():
            block_bank.hide()

            self.undo_stack.push(WorldBottomTile(self.world_map, block_bank.last_clicked_index))

            self._update_button_icon()

        block_bank.clicked.connect(_callback)

        block_bank.showNormal()

    def _change_anim_frame(self, new_count):
        """Preview a new animation tick count on the active world.

        Parameters
        ----------
        new_count : int
            Tick count between animation frames selected in the spinner.

        Notes
        -----
        Animation timing is the one metadata field previewed by direct
        mutation. :meth:`closeEvent` restores the original value before
        pushing the final :class:`~scribe.gui.commands.WorldTickPerFrame`
        command, so undo history rather than this preview callback owns
        persistence.
        """
        self.world_map.data.frame_tick_count = new_count

        self.world_map.palette_changed.emit()

    def _change_palette_index(self, new_index):
        """Push a palette change and refresh the preview tile icon.

        Parameters
        ----------
        new_index : int
            Palette index selected for the edited world map.

        Notes
        -----
        The palette index is an encoded world-data value. This path pushes an
        undo command immediately because both the world-map preview and the
        bottom-border tile icon should switch to the new palette as soon as the
        spinner changes.
        """
        self.undo_stack.push(WorldPaletteIndex(self.world_map, new_index))

        self._update_button_icon()

        self.world_map.palette_changed.emit()

    def _change_music_index(self, new_index: int):
        """Push a new music theme for the world.

        Parameters
        ----------
        new_index : int
        Index into the dialog's music-theme dropdown. The displayed name may
        be translated, but the command receives the stable SMB3 music value
        stored in item data so localization never becomes ROM identity.
        """
        music_index = self.music_dropdown.itemData(new_index)
        if music_index is None:
            return

        self.undo_stack.push(WorldMusicIndex(self.world_map, music_index))

    def closeEvent(self, event: QCloseEvent):
        """Commit valid staged edits before the dialog closes.

        The close handler is the boundary between speculative UI state and the
        editor's persistent undo history. It rejects invalid world-overview
        arrangements, records scroll and world-layout changes through undo
        commands, and rewrites the preview-only animation tick change as a
        command so the session stays reversible.

        Parameters
        ----------
        event : QCloseEvent
            Qt close event for the dialog.

        Notes
        -----
        Invalid world-overview arrangements are rejected by ignoring the close
        event. On success, the dialog pushes map-scroll, world-overview, and
        animation-timing commands onto the shared undo stack so the entire edit
        session remains reversible.
        """
        if not self.world_overview.valid():
            event.ignore()

            return

        should_scroll = self.scrolls_check_box.isChecked()

        if should_scroll != (self.world_map.data.map_scroll not in [0x00, NO_MAP_SCROLLING]):
            self.undo_stack.push(SetWorldScroll(self.world_map.data, should_scroll))

        self.world_overview.finalize(self.undo_stack)

        curr_tick_per_frame = self.world_map.data.frame_tick_count
        self.world_map.data.frame_tick_count = self.orig_tick_per_frame

        if self.orig_tick_per_frame != curr_tick_per_frame:
            self.undo_stack.push(WorldTickPerFrame(self.world_map, curr_tick_per_frame))
