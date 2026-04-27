Foundry GUI Modules
===================

These pages collect the Qt-facing modules that turn Foundry's ROM and level
model into an interactive editor workflow.

Start with the main window when you need the application shell, level and ROM
session management, or the handoff into command-driven editing. Follow the
dialogs and level-settings modules when you are tracing one focused editing
flow, and move into visualization, windows, and widgets when you need the
surfaces that render or inspect the active level state.

The GUI package is intentionally split by workflow role rather than by one big
widget tree. That means the useful path for maintainers is usually shell ->
dialog or command -> visualization or inspector surface, not simply parent
widget -> child widget. The pages below expose those major entry points first.

Architecture Guides
-------------------

- :doc:`/subsystems/foundry_gui_architecture` explains the editor shell's
  problem space, control flow, and long-lived GUI boundaries.
- :doc:`/subsystems/gui_editor_workflow` maps the broader maintainer route from
  :class:`~foundry.gui.FoundryMainWindow` into dialogs, views, and tool
  surfaces.

.. autosummary::
   :toctree: generated

   foundry.gui.FoundryMainWindow
   foundry.gui.MainWindow
   foundry.gui.ContextMenu
   foundry.gui.JumpList
   foundry.gui.ObjectDropdown
   foundry.gui.ObjectList
   foundry.gui.ObjectStatusBar
   foundry.gui.SpinnerPanel
   foundry.gui.WarningList
   foundry.gui.settings
   foundry.gui.dialogs.AboutWindow
   foundry.gui.dialogs.AutoSaveDialog
   foundry.gui.dialogs.CustomDialog
   foundry.gui.level_settings.auto_scroll_mixin
   foundry.gui.level_settings.boom_boom_mixin
   foundry.gui.level_settings.chest_exit_mixin
   foundry.gui.level_settings.level_settings_dialog
   foundry.gui.level_settings.pipe_pair_mixin
   foundry.gui.level_settings.settings_mixin
   foundry.gui.level_settings.white_mushroom_mixin
   foundry.gui.rom_settings.managed_levels_mixin
   foundry.gui.rom_settings.rom_settings_dialog
   foundry.gui.menus.debug_menu
   foundry.gui.menus.file_menu
   foundry.gui.menus.help_menu
   foundry.gui.menus.rom_menu
   foundry.gui.menus.view_menu
   foundry.gui.commands
   foundry.gui.visualization.MainView
   foundry.gui.visualization.SelectionSquare
   foundry.gui.visualization.level.LevelView
   foundry.gui.visualization.level.LevelDrawer
   foundry.gui.visualization.level.AutoScrollDrawer
   foundry.gui.visualization.world.WorldView
   foundry.gui.visualization.world.WorldDrawer
   foundry.gui.windows.LevelViewer
   foundry.gui.widgets.table_widget
