User Guide
==========

The user guide route points readers toward task-oriented manuals for Foundry
and Scribe. The Sphinx API and subsystem pages explain maintainer-facing code
structure; the manuals explain how the editor tools behave from a user's point
of view.

Manuals
-------

.. container:: doc-card-grid

   .. container:: doc-card

      **Foundry Manual**

      Download the :download:`Foundry manual <../manual/foundry/foundry-manual.pdf>`
      when you need level-editor workflows, menu behavior, and task-oriented
      guidance for editing SMB3 levels.

   .. container:: doc-card

      **Scribe Manual**

      Download the :download:`Scribe manual <../manual/scribe/scribe-manual.pdf>`
      when you need world-map editing workflows, Scribe controls, and map-data
      guidance.

Readable Manuals
----------------

The manuals are also available as Sphinx pages:

.. toctree::
   :maxdepth: 2

   user_guide/foundry_manual
   user_guide/scribe_manual

How To Use This Page
--------------------

Use manuals for user-facing behavior and Sphinx pages for maintainer-facing
architecture. When a code change affects editor behavior, update the relevant
API or subsystem page for maintainers and check whether the corresponding
manual should also change for users.

Enemy and item visuals are also available as a generated maintainer reference
in :doc:`subsystems/enemy_sprite_catalog`. Use it when a manual screenshot or
editor report names an enemy visually but you need the matching SMB3 object id.

Read This Next
--------------

.. rst-class:: route-list

- For Foundry editor architecture, read :doc:`subsystems/foundry_gui_architecture`.
- For generated Foundry GUI code reference, read :doc:`api/foundry_gui`.
- For enemy and item visual identification, read
  :doc:`subsystems/enemy_sprite_catalog`.
- For Scribe architecture, read :doc:`subsystems/scribe_gui_architecture`.
- For generated Scribe code reference, read :doc:`api/scribe_gui`.
- For API reference, read :doc:`api/index`.
