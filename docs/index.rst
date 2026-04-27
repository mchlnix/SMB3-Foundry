Foundry Documentation
=====================

.. rst-class:: hero

Foundry's documentation is the maintainer map for the level editor, Scribe
world-map tooling, and SMB3 parsing helpers. It connects API reference pages,
architecture notes, subsystem routes, and the user manuals so contributors can
move from a concrete symbol to the workflow it serves.

Start here when you need to understand how editor actions become model changes,
how ROM-backed data moves through parsers and renderers, or where a user-facing
feature should be documented after implementation.

.. container:: doc-card-grid

   .. container:: doc-card

      **API Reference**

      Use :doc:`api/index` when you know the package family or module name and
      need autodoc output, class contracts, or related symbols. Pair it with
      :doc:`subsystems/index` when you need the workflow guide beside the code.

   .. container:: doc-card

      **Subsystem Guides**

      Use :doc:`subsystems/index` when you need the workflow route from GUI to
      model, renderer, persistence, parser, or command handling. Each guide
      links back to the closest API reference so architecture and code stay
      side by side.

   .. container:: doc-card

      **Foundry Manual**

      Use :doc:`user_guide` to reach the Foundry manual for task-oriented
      editor behavior and user-facing workflows that should not be duplicated
      in API pages.

   .. container:: doc-card

      **Scribe Manual**

      Use :doc:`user_guide` to reach the Scribe manual for world-map editing
      behavior, map data workflows, and user-facing Scribe concepts.

Read This Next
--------------

.. rst-class:: route-list

- New to the codebase: start with :doc:`subsystems/gui_editor_workflow`, then
  follow :doc:`subsystems/level_world_model`.
- Working on ROM safety or reload behavior: start with
  :doc:`subsystems/rom_data_persistence`.
- Working on rendering or object visuals: start with
  :doc:`subsystems/graphics_rendering`, then follow the graphics API pages.
- Working on Scribe: start with :doc:`subsystems/scribe_gui_architecture`.
- Working on parsers: start with :doc:`subsystems/smb3parse_parser_architecture`.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   api/index
   subsystems/index
   user_guide
