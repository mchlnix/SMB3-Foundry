Foundry Features Architecture
=============================

Problem and Context
-------------------

The :mod:`foundry.features` family holds application behaviors that cross the
boundary between the GUI shell and the ROM-backed model without belonging to
either layer alone. These modules typically own lifecycle-sensitive work such
as playtest staging, update checks, or ROM reload handling.

Goals
-----

- Keep cross-cutting application behaviors out of the core model and out of
  random widgets.
- Make feature entry points explicit so startup, reload, and external-tool
  workflows remain traceable.
- Preserve clear handoffs back into the GUI shell and the game model.
- Keep each feature narrow enough that failures stay local.

Non-Goals
---------

- Become a second home for generic editor utilities.
- Replace the command stack or the model layer.
- Hide long-lived ownership that properly belongs in :mod:`foundry.gui` or
  :mod:`foundry.game`.

Current State
-------------

The current feature set is intentionally small. :mod:`foundry.features.instaplay`
stages a temporary ROM playtest workflow, :mod:`foundry.features.online_updates`
owns release-query and update-prompt policy, and
:mod:`foundry.features.rom_reload` handles ROM-refresh boundaries that would be
awkward to bury inside either the main window or the model layer.

Data Flow
---------

1. The GUI shell or startup code decides a feature should run.
2. The feature module reads the active settings, ROM session, or model state it
   needs.
3. The feature performs its focused external or lifecycle work.
4. Results are translated back into shell actions, dialogs, command replay, or
   refreshed model state.

Control Flow
------------

Feature control usually starts from :class:`foundry.gui.FoundryMainWindow` or a
menu or startup hook. The feature owns the middle section of the workflow, then
hands the result back to shell surfaces or model updates. That means the useful
trace is usually shell -> feature -> model or external integration point ->
shell follow-up.

Architectural Decisions
-----------------------

- Feature modules stay narrow and named by behavior, not by shared utility
  category.
- The shell triggers features, but the shell does not absorb their internal
  policy.
- Features may coordinate multiple layers, but they should not become the new
  source of truth for editor state.
- External integration points are isolated here so session lifecycle failures
  do not sprawl across unrelated GUI modules.

Read This Next
--------------

- Start with :mod:`foundry.features.rom_reload` for reload, state refresh, and
  replay-sensitive editor boundaries.
- Read :mod:`foundry.features.instaplay` for temporary ROM staging and emulator
  handoff.
- Continue to :mod:`foundry.features.online_updates` for startup-time or
  manual update checks and release-channel policy.
- Move back to :class:`foundry.gui.FoundryMainWindow` when the remaining issue
  is shell coordination rather than feature-local behavior.
