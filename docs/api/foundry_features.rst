Foundry Feature Modules
=======================

These pages collect application-level features that sit above the core model
but below the Qt shell.

Start here when you are tracing workflows that cut across the editor shell and
the ROM/model layers without belonging to one single widget or model object.
These modules own “application behaviors” such as hot-reload, update checking,
and instant playtest setup.

Each entry is a cross-cutting feature rather than a base abstraction. The
useful maintenance path is therefore editor shell -> feature -> ROM/model
integration point, especially when debugging session lifecycle, persistence
boundaries, or external-tool handoffs. Follow the feature page first when the
same user action touches window state, ROM-backed state, and an external
process or background task at once.

Architecture Guides
-------------------

- :doc:`/subsystems/foundry_features_architecture` explains why these features
  sit above the core model but below the application shell.
- :doc:`/subsystems/gui_editor_workflow` shows where feature modules re-enter
  the main editor workflow.
- :doc:`/subsystems/rom_data_persistence` covers the ROM-backed boundaries that
  features such as :mod:`foundry.features.rom_reload` must preserve.

.. autosummary::
   :toctree: generated

   foundry.features.instaplay
   foundry.features.online_updates
   foundry.features.rom_reload
