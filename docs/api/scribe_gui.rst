Scribe GUI Modules
==================

These pages collect the SMB3 Scribe GUI modules that own overworld editing,
world-map commands, and the companion Qt workflow layered beside Foundry.

Start with the main window and world overview when you need the top-level
editing flow. Follow the command, menu, and tool-window modules when you are
tracking how gestures become undoable world-map edits or how those edits fan
back out into focused editor widgets.

Architecture Guides
-------------------

- :doc:`/subsystems/scribe_gui_architecture` explains the overall Scribe shell
  and world-editing workflow.
- :doc:`/subsystems/scribe_commands_architecture` focuses on undoable overworld
  command flow.
- :doc:`/subsystems/scribe_tool_window_architecture` covers the inspector-style
  tool surfaces that hang off the main window.
- :doc:`/subsystems/scribe_menus_architecture` explains the menu routing layer
  and how it hands control into commands and dialogs.

.. autosummary::
   :toctree: generated

   scribe.gui
   scribe.gui.about_window
   scribe.gui.main_window
   scribe.gui.settings_dialog
   scribe.gui.world_overview
   scribe.gui.world_view_context_menu
   scribe.gui.edit_world_info
   scribe.gui.commands
   scribe.gui.tool_window
   scribe.gui.tool_window.tool_window
   scribe.gui.tool_window.level_pointer_list
   scribe.gui.tool_window.locks_list
   scribe.gui.tool_window.sprite_list
   scribe.gui.tool_window.block_picker
   scribe.gui.tool_window.table_widget
   scribe.gui.menus
   scribe.gui.menus.edit_menu
   scribe.gui.menus.view_menu
   scribe.gui.menus.help_menu
