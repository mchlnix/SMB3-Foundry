Enemy Sprite Catalog
====================

This catalog renders every SMB3 enemy/item definition in Foundry's enemy object set.
It is generated from ``data/objects.dat`` and ``data/gfx.png`` so the images match
the editor's static sprite metadata without requiring a loaded ROM, Qt palette state,
or a running Foundry window.

The catalog is visual-first: entries are grouped by what a maintainer is likely
trying to identify on screen. Raw IDs, dimensions, block indexes, and compatibility
clan/group metadata remain visible so the visual grouping can be audited against
the underlying SMB3 data.

.. note::

   ``MSG_NOTHING`` and ``MSG_CRASH`` rows are intentionally included. They are part
   of the enemy object-set table, even when the editor would normally hide them
   from placement workflows.

Generation Method
-----------------

- Source definitions: ``data/objects.dat`` bank ``0x10``.
- Source pixels: ``data/gfx.png``.
- Tile mapping: ``block_id % 64`` gives the tile column and
  ``48 + block_id // 64`` gives the tile row.
- Transparency: magenta mask pixels are converted to alpha.
- Manifest: :download:`enemy_catalog_manifest.json <../_static/images/enemy_catalog/enemy_catalog_manifest.json>`.

Visual Contact Sheets
---------------------

Bosses
~~~~~~

8 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/bosses.png
   :alt: Contact sheet for bosses in the SMB3 enemy catalog.

Ground Enemies
~~~~~~~~~~~~~~

29 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/ground-enemies.png
   :alt: Contact sheet for ground enemies in the SMB3 enemy catalog.

Flying Enemies
~~~~~~~~~~~~~~

11 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/flying-enemies.png
   :alt: Contact sheet for flying enemies in the SMB3 enemy catalog.

Aquatic Enemies
~~~~~~~~~~~~~~~

14 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/aquatic-enemies.png
   :alt: Contact sheet for aquatic enemies in the SMB3 enemy catalog.

Hazards and Projectiles
~~~~~~~~~~~~~~~~~~~~~~~

33 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/hazards-and-projectiles.png
   :alt: Contact sheet for hazards and projectiles in the SMB3 enemy catalog.

Platforms and Machinery
~~~~~~~~~~~~~~~~~~~~~~~

26 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/platforms-and-machinery.png
   :alt: Contact sheet for platforms and machinery in the SMB3 enemy catalog.

Pickups and Items
~~~~~~~~~~~~~~~~~

22 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/pickups-and-items.png
   :alt: Contact sheet for pickups and items in the SMB3 enemy catalog.

Exits and Controls
~~~~~~~~~~~~~~~~~~

7 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/exits-and-controls.png
   :alt: Contact sheet for exits and controls in the SMB3 enemy catalog.

Terrain and Environmental
~~~~~~~~~~~~~~~~~~~~~~~~~

20 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/terrain-and-environmental.png
   :alt: Contact sheet for terrain and environmental in the SMB3 enemy catalog.

Unknown and Placeholder Entries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

25 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/unknown-and-placeholder-entries.png
   :alt: Contact sheet for unknown and placeholder entries in the SMB3 enemy catalog.

Crash Entries
~~~~~~~~~~~~~

22 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/crash-entries.png
   :alt: Contact sheet for crash entries in the SMB3 enemy catalog.

Other Entries
~~~~~~~~~~~~~

20 entries.

.. image:: ../_static/images/enemy_catalog/contact_sheets/other-entries.png
   :alt: Contact sheet for other entries in the SMB3 enemy catalog.

Complete Entry Index
--------------------

.. raw:: html

   <div class="enemy-catalog-grid">
      <section class="enemy-catalog-category" id="enemy-category-bosses">
        <h3>Bosses</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-0e-world-x-boss-where-x-world.png" alt="Sprite preview for enemy ID 0x0e, World x Boss (where x = world)" />
            <h4>0x0e World x Boss (where x = world)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 6</p>
            <p><strong>Blocks:</strong> 0x07, 0x08, 0x17, 0x18</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-18-bowser.png" alt="Sprite preview for enemy ID 0x18, Bowser" />
            <h4>0x18 Bowser</h4>
            <p><strong>Size:</strong> 2x3 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x20, 0x21, 0x30, 0x31, 0x40, 0x41</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-2d-boss-bass-surface.png" alt="Sprite preview for enemy ID 0x2d, Boss Bass (surface)" />
            <h4>0x2d Boss Bass (surface)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x34, 0x35, 0x44, 0x45</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-4b-boom-boom.png" alt="Sprite preview for enemy ID 0x4b, Boom Boom" />
            <h4>0x4b Boom Boom</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 5</p>
            <p><strong>Blocks:</strong> 0x61, 0x62, 0x71, 0x72</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-4c-flying-boom-boom.png" alt="Sprite preview for enemy ID 0x4c, Flying Boom Boom" />
            <h4>0x4c Flying Boom Boom</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 5</p>
            <p><strong>Blocks:</strong> 0x63, 0x73</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-75-bowser-s-fireballs.png" alt="Sprite preview for enemy ID 0x75, Bowser&#x27;s Fireballs" />
            <h4>0x75 Bowser&#x27;s Fireballs</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x98</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-af-the-angry-sun.png" alt="Sprite preview for enemy ID 0xaf, The Angry Sun" />
            <h4>0xaf The Angry Sun</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 6</p>
            <p><strong>Blocks:</strong> 0x7d, 0x7e, 0x8d, 0x8e</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d0-lasers-use-with-bowser-statues.png" alt="Sprite preview for enemy ID 0xd0, Lasers (use with Bowser statues)" />
            <h4>0xd0 Lasers (use with Bowser statues)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x4c</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-ground-enemies">
        <h3>Ground Enemies</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-29-spike.png" alt="Sprite preview for enemy ID 0x29, Spike" />
            <h4>0x29 Spike</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0x25</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-2b-kuribo-s-goomba.png" alt="Sprite preview for enemy ID 0x2b, Kuribo&#x27;s Goomba" />
            <h4>0x2b Kuribo&#x27;s Goomba</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0x33, 0x43</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-3f-dry-bones.png" alt="Sprite preview for enemy ID 0x3f, Dry Bones" />
            <h4>0x3f Dry Bones</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 1</p>
            <p><strong>Blocks:</strong> 0x50, 0x60</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-40-buster-beetle.png" alt="Sprite preview for enemy ID 0x40, Buster Beetle" />
            <h4>0x40 Buster Beetle</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0x51</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-4f-jumping-chomp.png" alt="Sprite preview for enemy ID 0x4f, Jumping Chomp" />
            <h4>0x4f Jumping Chomp</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xce</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-50-bob-omb-about-to-blow-up.png" alt="Sprite preview for enemy ID 0x50, Bob-Omb (about to blow up)" />
            <h4>0x50 Bob-Omb (about to blow up)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x68</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-55-bob-omb.png" alt="Sprite preview for enemy ID 0x55, Bob-Omb" />
            <h4>0x55 Bob-Omb</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0x68</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-68-upside-down-buzzy-beetle.png" alt="Sprite preview for enemy ID 0x68, Upside-down Buzzy Beetle" />
            <h4>0x68 Upside-down Buzzy Beetle</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0x83</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-69-upside-down-spiny.png" alt="Sprite preview for enemy ID 0x69, Upside-down Spiny" />
            <h4>0x69 Upside-down Spiny</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x84</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-6b-pile-driver-micro-goomba.png" alt="Sprite preview for enemy ID 0x6b, Pile Driver Micro-Goomba" />
            <h4>0x6b Pile Driver Micro-Goomba</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x88</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-6c-green-koopa-troopa.png" alt="Sprite preview for enemy ID 0x6c, Green Koopa Troopa" />
            <h4>0x6c Green Koopa Troopa</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x89, 0x99</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-6d-red-koopa-troopa.png" alt="Sprite preview for enemy ID 0x6d, Red Koopa Troopa" />
            <h4>0x6d Red Koopa Troopa</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x8a, 0x9a</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-70-buzzy-beetle.png" alt="Sprite preview for enemy ID 0x70, Buzzy Beetle" />
            <h4>0x70 Buzzy Beetle</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0x9d</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-71-spiny.png" alt="Sprite preview for enemy ID 0x71, Spiny" />
            <h4>0x71 Spiny</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0x9e</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-72-goomba.png" alt="Sprite preview for enemy ID 0x72, Goomba" />
            <h4>0x72 Goomba</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x97</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-7a-giant-green-koopa-troopa.png" alt="Sprite preview for enemy ID 0x7a, Giant Green Koopa Troopa" />
            <h4>0x7a Giant Green Koopa Troopa</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xa8, 0xa9, 0xb8, 0xb9</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-7b-giant-red-koopa-troopa.png" alt="Sprite preview for enemy ID 0x7b, Giant Red Koopa Troopa" />
            <h4>0x7b Giant Red Koopa Troopa</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xaa, 0xab, 0xba, 0xbb</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-7c-giant-goomba.png" alt="Sprite preview for enemy ID 0x7c, Giant Goomba" />
            <h4>0x7c Giant Goomba</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xac, 0xad, 0xbc, 0xbd</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-81-hammer-brother.png" alt="Sprite preview for enemy ID 0x81, Hammer Brother" />
            <h4>0x81 Hammer Brother</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 1</p>
            <p><strong>Blocks:</strong> 0xc1, 0xd1</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-84-red-spiny-egg.png" alt="Sprite preview for enemy ID 0x84, Red Spiny Egg" />
            <h4>0x84 Red Spiny Egg</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xc8</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-85-green-spiny-egg.png" alt="Sprite preview for enemy ID 0x85, Green Spiny Egg" />
            <h4>0x85 Green Spiny Egg</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xc9</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-86-sledge-brother.png" alt="Sprite preview for enemy ID 0x86, Sledge Brother" />
            <h4>0x86 Sledge Brother</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 1</p>
            <p><strong>Blocks:</strong> 0xca, 0xcb, 0xda, 0xdb</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-89-chain-chomp.png" alt="Sprite preview for enemy ID 0x89, Chain Chomp" />
            <h4>0x89 Chain Chomp</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0xde, 0xce</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-8a-thwomp-normal.png" alt="Sprite preview for enemy ID 0x8a, Thwomp (normal)" />
            <h4>0x8a Thwomp (normal)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x53, 0x54, 0x10, 0x11</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-8b-thwomp-moves-left.png" alt="Sprite preview for enemy ID 0x8b, Thwomp (moves left)" />
            <h4>0x8b Thwomp (moves left)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x53, 0x54, 0x10, 0x11</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-8c-thwomp-moves-right.png" alt="Sprite preview for enemy ID 0x8c, Thwomp (moves right)" />
            <h4>0x8c Thwomp (moves right)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x53, 0x54, 0x10, 0x11</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-8d-thwomp-moves-up.png" alt="Sprite preview for enemy ID 0x8d, Thwomp (moves up)" />
            <h4>0x8d Thwomp (moves up)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x53, 0x54, 0x10, 0x11</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-8e-thwomp-moves-diagonally-up-and-left.png" alt="Sprite preview for enemy ID 0x8e, Thwomp (moves diagonally up and left)" />
            <h4>0x8e Thwomp (moves diagonally up and left)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x53, 0x54, 0x10, 0x11</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-8f-thwomp-moves-diagonally-down-and-left.png" alt="Sprite preview for enemy ID 0x8f, Thwomp (moves diagonally down and left)" />
            <h4>0x8f Thwomp (moves diagonally down and left)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x53, 0x54, 0x10, 0x11</p>
            <p><strong>Notes:</strong> none</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-flying-enemies">
        <h3>Flying Enemies</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-6e-green-koopa-paratroopa-bounces.png" alt="Sprite preview for enemy ID 0x6e, Green Koopa Paratroopa (bounces)" />
            <h4>0x6e Green Koopa Paratroopa (bounces)</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x8c, 0x9c</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-6f-red-koopa-paratroopa.png" alt="Sprite preview for enemy ID 0x6f, Red Koopa Paratroopa" />
            <h4>0x6f Red Koopa Paratroopa</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x8f, 0x9f</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-73-para-goomba.png" alt="Sprite preview for enemy ID 0x73, Para-Goomba" />
            <h4>0x73 Para-Goomba</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa0, 0xa1, 0xb0, 0xb1</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-74-para-goomba-with-micro-goombas.png" alt="Sprite preview for enemy ID 0x74, Para-Goomba with Micro-Goombas" />
            <h4>0x74 Para-Goomba with Micro-Goombas</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa2, 0xa3, 0xb2, 0xb3</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-7e-giant-green-koopa-paratroopa.png" alt="Sprite preview for enemy ID 0x7e, Giant Green Koopa Paratroopa" />
            <h4>0x7e Giant Green Koopa Paratroopa</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xb4, 0xb5, 0xc4, 0xc5</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-80-green-koopa-paratroopa-doesn-t-bounce.png" alt="Sprite preview for enemy ID 0x80, Green Koopa Paratroopa (doesn&#x27;t bounce)" />
            <h4>0x80 Green Koopa Paratroopa (doesn&#x27;t bounce)</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x8c, 0x9c</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-82-boomerang-brother.png" alt="Sprite preview for enemy ID 0x82, Boomerang Brother" />
            <h4>0x82 Boomerang Brother</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 1</p>
            <p><strong>Blocks:</strong> 0xc2, 0xd2</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-83-lakitu.png" alt="Sprite preview for enemy ID 0x83, Lakitu" />
            <h4>0x83 Lakitu</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0xc3, 0xd3</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-9f-para-beetle.png" alt="Sprite preview for enemy ID 0x9f, Para-Beetle" />
            <h4>0x9f Para-Beetle</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 2</p>
            <p><strong>Blocks:</strong> 0xdd</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b6-lakitu-boundary.png" alt="Sprite preview for enemy ID 0xb6, Lakitu boundary" />
            <h4>0xb6 Lakitu boundary</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x3d</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d1-3-green-koopa-paratroopas.png" alt="Sprite preview for enemy ID 0xd1, 3 Green Koopa Paratroopas" />
            <h4>0xd1 3 Green Koopa Paratroopas</h4>
            <p><strong>Size:</strong> 3x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x8c, 0x8c, 0x8c, 0x9c, 0x9c, 0x9c</p>
            <p><strong>Notes:</strong> none</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-aquatic-enemies">
        <h3>Aquatic Enemies</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-17-spiky-cheep-cheep.png" alt="Sprite preview for enemy ID 0x17, Spiky Cheep-Cheep" />
            <h4>0x17 Spiky Cheep-Cheep</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x09</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-3b-surface-cheep-cheep-swims-along-surface.png" alt="Sprite preview for enemy ID 0x3b, Surface Cheep-Cheep (swims along surface)" />
            <h4>0x3b Surface Cheep-Cheep (swims along surface)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x48</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-42-jumping-cheep-cheep-3-jumps-up-and-right.png" alt="Sprite preview for enemy ID 0x42, Jumping Cheep-Cheep (3 jumps, up and right)" />
            <h4>0x42 Jumping Cheep-Cheep (3 jumps, up and right)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x48</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-43-jumping-cheep-cheep-2-jumps-down-and-right.png" alt="Sprite preview for enemy ID 0x43, Jumping Cheep-Cheep (2 jumps, down and right)" />
            <h4>0x43 Jumping Cheep-Cheep (2 jumps, down and right)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x48</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-48-baby-cheep-cheep.png" alt="Sprite preview for enemy ID 0x48, Baby Cheep-Cheep" />
            <h4>0x48 Baby Cheep-Cheep</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x5b</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-61-blooper-with-babies.png" alt="Sprite preview for enemy ID 0x61, Blooper (with babies)" />
            <h4>0x61 Blooper (with babies)</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x7b, 0x8b</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-62-blooper.png" alt="Sprite preview for enemy ID 0x62, Blooper" />
            <h4>0x62 Blooper</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x7c</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-63-big-bertha-underwater.png" alt="Sprite preview for enemy ID 0x63, Big Bertha (underwater)" />
            <h4>0x63 Big Bertha (underwater)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x34, 0x35, 0x44, 0x45</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-64-surface-cheep-cheep-jumps-out-of-water.png" alt="Sprite preview for enemy ID 0x64, Surface Cheep-Cheep (jumps out of water)" />
            <h4>0x64 Surface Cheep-Cheep (jumps out of water)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x48</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-6a-blooper-nanny.png" alt="Sprite preview for enemy ID 0x6a, Blooper Nanny" />
            <h4>0x6a Blooper Nanny</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x87</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-76-falling-cheep-cheep.png" alt="Sprite preview for enemy ID 0x76, Falling Cheep-Cheep" />
            <h4>0x76 Falling Cheep-Cheep</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x48</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-77-cheep-cheep.png" alt="Sprite preview for enemy ID 0x77, Cheep-Cheep" />
            <h4>0x77 Cheep-Cheep</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa5</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-88-yellow-cheep-cheep.png" alt="Sprite preview for enemy ID 0x88, Yellow Cheep-Cheep" />
            <h4>0x88 Yellow Cheep-Cheep</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xcd</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d2-3-yellow-cheep-cheeps.png" alt="Sprite preview for enemy ID 0xd2, 3 Yellow Cheep-Cheeps" />
            <h4>0xd2 3 Yellow Cheep-Cheeps</h4>
            <p><strong>Size:</strong> 1x3 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xcd, 0xcd, 0xcd</p>
            <p><strong>Notes:</strong> none</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-hazards-and-projectiles">
        <h3>Hazards and Projectiles</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-3d-walking-ptooie-spits-fireballs.png" alt="Sprite preview for enemy ID 0x3d, Walking Ptooie (spits fireballs)" />
            <h4>0x3d Walking Ptooie (spits fireballs)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0x2f</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-51-double-rotodisc-rotates-counterclockwise.png" alt="Sprite preview for enemy ID 0x51, Double Rotodisc (rotates counterclockwise)" />
            <h4>0x51 Double Rotodisc (rotates counterclockwise)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x74</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-53-stray-podoboo.png" alt="Sprite preview for enemy ID 0x53, Stray Podoboo" />
            <h4>0x53 Stray Podoboo</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x67</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-5a-single-rotodisc-rotates-clockwise.png" alt="Sprite preview for enemy ID 0x5a, Single Rotodisc (rotates clockwise)" />
            <h4>0x5a Single Rotodisc (rotates clockwise)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x74</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-5b-single-rotodisc-rotates-counterclockwise.png" alt="Sprite preview for enemy ID 0x5b, Single Rotodisc (rotates counterclockwise)" />
            <h4>0x5b Single Rotodisc (rotates counterclockwise)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x74</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-5e-double-rotodisc-rotates-both-ways-starting-at-sides.png" alt="Sprite preview for enemy ID 0x5e, Double Rotodisc (rotates both ways, starting at sides)" />
            <h4>0x5e Double Rotodisc (rotates both ways, starting at sides)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x74</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-5f-double-rotodisc-rotates-both-ways-starting-at-top.png" alt="Sprite preview for enemy ID 0x5f, Double Rotodisc (rotates both ways, starting at top)" />
            <h4>0x5f Double Rotodisc (rotates both ways, starting at top)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x74</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-60-double-rotodisc-rotates-clockwise.png" alt="Sprite preview for enemy ID 0x60, Double Rotodisc (rotates clockwise)" />
            <h4>0x60 Double Rotodisc (rotates clockwise)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x74</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-78-still-bullet-bill.png" alt="Sprite preview for enemy ID 0x78, Still Bullet Bill" />
            <h4>0x78 Still Bullet Bill</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa6</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-9e-podoboo-comes-out-of-lava.png" alt="Sprite preview for enemy ID 0x9e, Podoboo (comes out of lava)" />
            <h4>0x9e Podoboo (comes out of lava)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x67</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b0-still-big-bullet.png" alt="Sprite preview for enemy ID 0xb0, Still Big Bullet" />
            <h4>0xb0 Still Big Bullet</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xd4, 0xd5, 0xe4, 0xe5</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b4-infinite-flying-cheep-cheeps.png" alt="Sprite preview for enemy ID 0xb4, Infinite flying Cheep-Cheeps" />
            <h4>0xb4 Infinite flying Cheep-Cheeps</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa4</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b5-infinite-spiky-cheep-cheeps.png" alt="Sprite preview for enemy ID 0xb5, Infinite Spiky Cheep-Cheeps" />
            <h4>0xb5 Infinite Spiky Cheep-Cheeps</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 8</p>
            <p><strong>Blocks:</strong> 0x1a</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b7-infinite-para-beetles.png" alt="Sprite preview for enemy ID 0xb7, Infinite Para-Beetles" />
            <h4>0xb7 Infinite Para-Beetles</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 2</p>
            <p><strong>Blocks:</strong> 0x49</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-bb-stops-infinite-flying-or-spiky-cheep-cheeps.png" alt="Sprite preview for enemy ID 0xbb, Stops infinite flying or spiky Cheep-Cheeps" />
            <h4>0xbb Stops infinite flying or spiky Cheep-Cheeps</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-bc-bullet-bills.png" alt="Sprite preview for enemy ID 0xbc, Bullet Bills" />
            <h4>0xbc Bullet Bills</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa6</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-bf-cross-shaped-bullet-shots.png" alt="Sprite preview for enemy ID 0xbf, Cross-shaped bullet shots" />
            <h4>0xbf Cross-shaped bullet shots</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c0-infinite-goombas-leftward.png" alt="Sprite preview for enemy ID 0xc0, Infinite Goombas (leftward)" />
            <h4>0xc0 Infinite Goombas (leftward)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x5f</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c1-infinite-goombas-rightward.png" alt="Sprite preview for enemy ID 0xc1, Infinite Goombas (rightward)" />
            <h4>0xc1 Infinite Goombas (rightward)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x5f</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c2-bullet-shots-leftward.png" alt="Sprite preview for enemy ID 0xc2, Bullet Shots (leftward)" />
            <h4>0xc2 Bullet Shots (leftward)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c3-big-bullet-shots-leftward.png" alt="Sprite preview for enemy ID 0xc3, Big Bullet Shots (leftward)" />
            <h4>0xc3 Big Bullet Shots (leftward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0xd4, 0xd5, 0xe4, 0xe5</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c4-bullet-shots-up-left.png" alt="Sprite preview for enemy ID 0xc4, Bullet Shots (up/left)" />
            <h4>0xc4 Bullet Shots (up/left)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c5-bullet-shots-up-right.png" alt="Sprite preview for enemy ID 0xc5, Bullet Shots (up/right)" />
            <h4>0xc5 Bullet Shots (up/right)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c6-bullet-shots-down-left.png" alt="Sprite preview for enemy ID 0xc6, Bullet Shots (down/left)" />
            <h4>0xc6 Bullet Shots (down/left)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c7-bullet-shots-down-right.png" alt="Sprite preview for enemy ID 0xc7, Bullet Shots (down/right)" />
            <h4>0xc7 Bullet Shots (down/right)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c8-bullet-shots-up-left.png" alt="Sprite preview for enemy ID 0xc8, Bullet Shots (up/left)" />
            <h4>0xc8 Bullet Shots (up/left)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-c9-bullet-shots-up-right.png" alt="Sprite preview for enemy ID 0xc9, Bullet Shots (up/right)" />
            <h4>0xc9 Bullet Shots (up/right)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ca-bullet-shots-down-left.png" alt="Sprite preview for enemy ID 0xca, Bullet Shots (down/left)" />
            <h4>0xca Bullet Shots (down/left)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-cb-bullet-shots-down-right.png" alt="Sprite preview for enemy ID 0xcb, Bullet Shots (down/right)" />
            <h4>0xcb Bullet Shots (down/right)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-cc-bullet-shots-rightward.png" alt="Sprite preview for enemy ID 0xcc, Bullet Shots (rightward)" />
            <h4>0xcc Bullet Shots (rightward)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x77</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-cd-big-bullet-shots-rightward.png" alt="Sprite preview for enemy ID 0xcd, Big Bullet Shots (rightward)" />
            <h4>0xcd Big Bullet Shots (rightward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0xd4, 0xd5, 0xe4, 0xe5</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ce-infinite-bob-ombs-leftward-use-with-bullet-shooters.png" alt="Sprite preview for enemy ID 0xce, Infinite Bob-Ombs (leftward) (use with bullet shooters)" />
            <h4>0xce Infinite Bob-Ombs (leftward) (use with bullet shooters)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0x16</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-cf-infinite-bob-ombs-rightward-use-with-bullet-shooters.png" alt="Sprite preview for enemy ID 0xcf, Infinite Bob-Ombs (rightward) (use with bullet shooters)" />
            <h4>0xcf Infinite Bob-Ombs (rightward) (use with bullet shooters)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 4</p>
            <p><strong>Blocks:</strong> 0x16</p>
            <p><strong>Notes:</strong> none</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-platforms-and-machinery">
        <h3>Platforms and Machinery</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-24-leftward-moving-cloud-platform-fast.png" alt="Sprite preview for enemy ID 0x24, Leftward-moving cloud platform (fast)" />
            <h4>0x24 Leftward-moving cloud platform (fast)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x26, 0x27, 0x28</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-26-still-wooden-platform-moves-right-when-stepped-on.png" alt="Sprite preview for enemy ID 0x26, Still wooden platform (moves right when stepped on)" />
            <h4>0x26 Still wooden platform (moves right when stepped on)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-27-wooden-platform-moves-back-and-forth-a-lot.png" alt="Sprite preview for enemy ID 0x27, Wooden platform - moves back and forth (a lot)" />
            <h4>0x27 Wooden platform - moves back and forth (a lot)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-28-wooden-platform-moves-up-and-down-a-lot.png" alt="Sprite preview for enemy ID 0x28, Wooden platform - moves up and down (a lot)" />
            <h4>0x28 Wooden platform - moves up and down (a lot)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-2c-leftward-moving-cloud-platform-slow.png" alt="Sprite preview for enemy ID 0x2c, Leftward-moving cloud platform (slow)" />
            <h4>0x2c Leftward-moving cloud platform (slow)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x26, 0x27, 0x28</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-2e-upward-moving-circle-block-platform.png" alt="Sprite preview for enemy ID 0x2e, Upward-moving Circle Block platform" />
            <h4>0x2e Upward-moving Circle Block platform</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x36, 0x36</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-36-wooden-platform-moves-left-falls-when-stepped-on.png" alt="Sprite preview for enemy ID 0x36, Wooden platform - moves left,falls when stepped on" />
            <h4>0x36 Wooden platform - moves left,falls when stepped on</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-37-wooden-platform-moves-back-and-forth-a-little.png" alt="Sprite preview for enemy ID 0x37, Wooden platform - moves back and forth (a little)" />
            <h4>0x37 Wooden platform - moves back and forth (a little)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-38-wooden-platform-moves-up-and-down-a-little.png" alt="Sprite preview for enemy ID 0x38, Wooden platform - moves up and down (a little)" />
            <h4>0x38 Wooden platform - moves up and down (a little)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-3a-falling-circle-block-platform.png" alt="Sprite preview for enemy ID 0x3a, Falling Circle Block platform" />
            <h4>0x3a Falling Circle Block platform</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x36, 0x36</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-3c-wired-platform-follows-platform-wires.png" alt="Sprite preview for enemy ID 0x3c, Wired platform (follows platform wires)" />
            <h4>0x3c Wired platform (follows platform wires)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 2</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-3e-floating-platform-floats-in-water.png" alt="Sprite preview for enemy ID 0x3e, Floating platform (floats in water)" />
            <h4>0x3e Floating platform (floats in water)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-44-falling-platform-falls-when-stepped-on.png" alt="Sprite preview for enemy ID 0x44, Falling Platform (falls when stepped on)" />
            <h4>0x44 Falling Platform (falls when stepped on)</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 2</p>
            <p><strong>Blocks:</strong> 0x37, 0x38, 0x39</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-5d-tornado.png" alt="Sprite preview for enemy ID 0x5d, Tornado" />
            <h4>0x5d Tornado</h4>
            <p><strong>Size:</strong> 4x8 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x76, 0x00, 0x00, 0x76, 0x76, 0x76, 0x00, 0x76, 0x76, 0x00, 0x00, 0x76, 0x76, 0x00, 0x00, 0x00, 0x76, 0x00, 0x00, 0x76, 0x00, 0x00</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-90-spinning-platform-step-activated.png" alt="Sprite preview for enemy ID 0x90, Spinning Platform (step-activated)" />
            <h4>0x90 Spinning Platform (step-activated)</h4>
            <p><strong>Size:</strong> 4x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xf6, 0xf5, 0xf4, 0xf5</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-91-spinning-platform-constant.png" alt="Sprite preview for enemy ID 0x91, Spinning Platform (constant)" />
            <h4>0x91 Spinning Platform (constant)</h4>
            <p><strong>Size:</strong> 4x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xf6, 0xf5, 0xf7, 0xf5</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-92-spinning-platform-periodical-clockwise.png" alt="Sprite preview for enemy ID 0x92, Spinning Platform (periodical clockwise)" />
            <h4>0x92 Spinning Platform (periodical clockwise)</h4>
            <p><strong>Size:</strong> 4x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xf6, 0xf5, 0xf8, 0xf5</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-93-spinning-platform-periodical-counterclockwise.png" alt="Sprite preview for enemy ID 0x93, Spinning Platform (periodical counterclockwise)" />
            <h4>0x93 Spinning Platform (periodical counterclockwise)</h4>
            <p><strong>Size:</strong> 4x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xf6, 0xf5, 0xf9, 0xf5</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-9d-upward-rocket-engine.png" alt="Sprite preview for enemy ID 0x9d, Upward Rocket Engine" />
            <h4>0x9d Upward Rocket Engine</h4>
            <p><strong>Size:</strong> 1x3 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 2</p>
            <p><strong>Blocks:</strong> 0x1c, 0x2c, 0x3c</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a8-auto-moving-upward-directional-platform.png" alt="Sprite preview for enemy ID 0xa8, Auto-moving upward directional platform" />
            <h4>0xa8 Auto-moving upward directional platform</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x0d, 0x0e</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a9-auto-moving-multi-directional-platform.png" alt="Sprite preview for enemy ID 0xa9, Auto-moving multi-directional platform" />
            <h4>0xa9 Auto-moving multi-directional platform</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x1d, 0x1e</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-aa-propeller.png" alt="Sprite preview for enemy ID 0xaa, Propeller" />
            <h4>0xaa Propeller</h4>
            <p><strong>Size:</strong> 1x3 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x100, 0x101, 0x102</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ac-leftward-rocket-engine.png" alt="Sprite preview for enemy ID 0xac, Leftward Rocket Engine" />
            <h4>0xac Leftward Rocket Engine</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 2</p>
            <p><strong>Blocks:</strong> 0x22, 0x23, 0x24</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b1-rightward-rocket-engine.png" alt="Sprite preview for enemy ID 0xb1, Rightward Rocket Engine" />
            <h4>0xb1 Rightward Rocket Engine</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 2</p>
            <p><strong>Blocks:</strong> 0x78, 0x79, 0x7a</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b2-downward-rocket-engine.png" alt="Sprite preview for enemy ID 0xb2, Downward Rocket Engine" />
            <h4>0xb2 Downward Rocket Engine</h4>
            <p><strong>Size:</strong> 1x3 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 2</p>
            <p><strong>Blocks:</strong> 0x65, 0x75, 0x64</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b9-infinite-leftward-moving-falling-platforms.png" alt="Sprite preview for enemy ID 0xb9, Infinite leftward-moving falling platforms" />
            <h4>0xb9 Infinite leftward-moving falling platforms</h4>
            <p><strong>Size:</strong> 3x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 2</p>
            <p><strong>Blocks:</strong> 0x37, 0x7f, 0x39</p>
            <p><strong>Notes:</strong> none</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-pickups-and-items">
        <h3>Pickups and Items</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-07-mushroom-house-with-warp-whistle-entrance.png" alt="Sprite preview for enemy ID 0x07, Mushroom House with Warp Whistle entrance" />
            <h4>0x07 Mushroom House with Warp Whistle entrance</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x46</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-09-ship-anchor.png" alt="Sprite preview for enemy ID 0x09, Ship Anchor" />
            <h4>0x09 Ship Anchor</h4>
            <p><strong>Size:</strong> 3x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x00, 0x106, 0x00, 0x103, 0x104, 0x105</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-0b-stray-1-up.png" alt="Sprite preview for enemy ID 0x0b, Stray 1-up" />
            <h4>0x0b Stray 1-up</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x04</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-0c-stray-star.png" alt="Sprite preview for enemy ID 0x0c, Stray Star" />
            <h4>0x0c Stray Star</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x05</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-0d-stray-mushroom.png" alt="Sprite preview for enemy ID 0x0d, Stray Mushroom" />
            <h4>0x0d Stray Mushroom</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x06</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-19-stray-flower.png" alt="Sprite preview for enemy ID 0x19, Stray Flower" />
            <h4>0x19 Stray Flower</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x13</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-1c-stray-mushroom.png" alt="Sprite preview for enemy ID 0x1c, Stray Mushroom" />
            <h4>0x1c Stray Mushroom</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x06</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-1e-stray-leaf.png" alt="Sprite preview for enemy ID 0x1e, Stray Leaf" />
            <h4>0x1e Stray Leaf</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x15</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-1f-stray-vine.png" alt="Sprite preview for enemy ID 0x1f, Stray Vine" />
            <h4>0x1f Stray Vine</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x19</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-21-flashing-mushroom.png" alt="Sprite preview for enemy ID 0x21, Flashing Mushroom" />
            <h4>0x21 Flashing Mushroom</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x0a</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-22-flashing-flower.png" alt="Sprite preview for enemy ID 0x22, Flashing Flower" />
            <h4>0x22 Flashing Flower</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x0b</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-23-flashing-star.png" alt="Sprite preview for enemy ID 0x23, Flashing Star" />
            <h4>0x23 Flashing Star</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x0c</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-41-goal-card.png" alt="Sprite preview for enemy ID 0x41, Goal Card" />
            <h4>0x41 Goal Card</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x52</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-79-stray-missile-bill.png" alt="Sprite preview for enemy ID 0x79, Stray Missile Bill" />
            <h4>0x79 Stray Missile Bill</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa7</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-94-giant-block-with-3-1-ups.png" alt="Sprite preview for enemy ID 0x94, Giant &#x27;?&#x27; Block with 3 1-ups" />
            <h4>0x94 Giant &#x27;?&#x27; Block with 3 1-ups</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xec, 0xed, 0xfc, 0xfd</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-95-giant-block-with-mushroom.png" alt="Sprite preview for enemy ID 0x95, Giant &#x27;?&#x27; Block with Mushroom" />
            <h4>0x95 Giant &#x27;?&#x27; Block with Mushroom</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xee, 0xef, 0xfe, 0xff</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-96-giant-block-with-flower.png" alt="Sprite preview for enemy ID 0x96, Giant &#x27;?&#x27; Block with Flower" />
            <h4>0x96 Giant &#x27;?&#x27; Block with Flower</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xea, 0xeb, 0xfa, 0xfb</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-97-giant-block-with-leaf.png" alt="Sprite preview for enemy ID 0x97, Giant &#x27;?&#x27; Block with Leaf" />
            <h4>0x97 Giant &#x27;?&#x27; Block with Leaf</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xd8, 0xd9, 0xe8, 0xe9</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-98-giant-block-with-tanooki-suit.png" alt="Sprite preview for enemy ID 0x98, Giant &#x27;?&#x27; Block with Tanooki Suit" />
            <h4>0x98 Giant &#x27;?&#x27; Block with Tanooki Suit</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xd6, 0xd7, 0xe6, 0xe7</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-99-giant-block-with-frog-suit.png" alt="Sprite preview for enemy ID 0x99, Giant &#x27;?&#x27; Block with Frog Suit" />
            <h4>0x99 Giant &#x27;?&#x27; Block with Frog Suit</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xe2, 0xe3, 0xf2, 0xf3</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-9a-giant-block-with-hammer-bros-suit.png" alt="Sprite preview for enemy ID 0x9a, Giant &#x27;?&#x27; Block with Hammer Bros. Suit" />
            <h4>0x9a Giant &#x27;?&#x27; Block with Hammer Bros. Suit</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xe0, 0xe1, 0xf0, 0xf1</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d4-hidden-enables-white-mushroom-house.png" alt="Sprite preview for enemy ID 0xd4, (Hidden) Enables White Mushroom House" />
            <h4>0xd4 (Hidden) Enables White Mushroom House</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x47</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-exits-and-controls">
        <h3>Exits and Controls</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-08-invisible-door-appears-when-you-hit-a-p-switch.png" alt="Sprite preview for enemy ID 0x08, Invisible door (appears when you hit a P-switch)" />
            <h4>0x08 Invisible door (appears when you hit a P-switch)</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 1</p>
            <p><strong>Blocks:</strong> 0x2a, 0x2b</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-25-changes-exit-location-on-map-works-on-warp-pipe-levels.png" alt="Sprite preview for enemy ID 0x25, Changes exit location on map (works on warp pipe levels)" />
            <h4>0x25 Changes exit location on map (works on warp pipe levels)</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-46-pipe-ptooie.png" alt="Sprite preview for enemy ID 0x46, Pipe Ptooie" />
            <h4>0x46 Pipe Ptooie</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0x117, 0x118, 0x119, 0x11a</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-52-treasure-chest.png" alt="Sprite preview for enemy ID 0x52, Treasure Chest" />
            <h4>0x52 Treasure Chest</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x66</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ba-hidden-makes-treasure-chest-end-the-level.png" alt="Sprite preview for enemy ID 0xba, (Hidden) Makes treasure chest end the level" />
            <h4>0xba (Hidden) Makes treasure chest end the level</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d3-autoscrolling.png" alt="Sprite preview for enemy ID 0xd3, Autoscrolling" />
            <h4>0xd3 Autoscrolling</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x93</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d6-hidden-sets-reward-item-in-treasure-chests.png" alt="Sprite preview for enemy ID 0xd6, (Hidden) Sets reward item in treasure chests" />
            <h4>0xd6 (Hidden) Sets reward item in treasure chests</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-terrain-and-environmental">
        <h3>Terrain and Environmental</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-06-colored-note-block.png" alt="Sprite preview for enemy ID 0x06, Colored note block" />
            <h4>0x06 Colored note block</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x14</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-1b-colored-note-block.png" alt="Sprite preview for enemy ID 0x1b, Colored note block" />
            <h4>0x1b Colored note block</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x14</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-33-nipper-plant.png" alt="Sprite preview for enemy ID 0x33, Nipper Plant" />
            <h4>0x33 Nipper Plant</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0x2f</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-39-walking-nipper-plant.png" alt="Sprite preview for enemy ID 0x39, Walking Nipper Plant" />
            <h4>0x39 Walking Nipper Plant</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0x2f</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-56-leftward-piranha-plant.png" alt="Sprite preview for enemy ID 0x56, Leftward Piranha Plant" />
            <h4>0x56 Leftward Piranha Plant</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x11b, 0x11c, 0x11d, 0x11e</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-57-rightward-piranha-plant.png" alt="Sprite preview for enemy ID 0x57, Rightward Piranha Plant" />
            <h4>0x57 Rightward Piranha Plant</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x11f, 0x120, 0x121, 0x122</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-58-fire-chomp.png" alt="Sprite preview for enemy ID 0x58, Fire Chomp" />
            <h4>0x58 Fire Chomp</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 2</p>
            <p><strong>Blocks:</strong> 0x6f</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-59-fire-snake.png" alt="Sprite preview for enemy ID 0x59, Fire Snake" />
            <h4>0x59 Fire Snake</h4>
            <p><strong>Size:</strong> 1x3 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 2</p>
            <p><strong>Blocks:</strong> 0x70, 0x80, 0x90</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-67-lava-lotus.png" alt="Sprite preview for enemy ID 0x67, Lava Lotus" />
            <h4>0x67 Lava Lotus</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 4</p>
            <p><strong>Blocks:</strong> 0x85, 0x86, 0x95, 0x96</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-7d-giant-green-piranha-plant.png" alt="Sprite preview for enemy ID 0x7d, Giant Green Piranha Plant" />
            <h4>0x7d Giant Green Piranha Plant</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xae, 0xaf, 0xbe, 0xbf</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-7f-giant-red-piranha-plant.png" alt="Sprite preview for enemy ID 0x7f, Giant Red Piranha Plant" />
            <h4>0x7f Giant Red Piranha Plant</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0xb6, 0xb7, 0xc6, 0xc7</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-87-fire-brother.png" alt="Sprite preview for enemy ID 0x87, Fire Brother" />
            <h4>0x87 Fire Brother</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 1</p>
            <p><strong>Blocks:</strong> 0xcc, 0xdc</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a0-green-piranha-plant-upward.png" alt="Sprite preview for enemy ID 0xa0, Green Piranha Plant (upward)" />
            <h4>0xa0 Green Piranha Plant (upward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x10b, 0x10c, 0x02, 0x03</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a1-green-piranha-plant-downward.png" alt="Sprite preview for enemy ID 0xa1, Green Piranha Plant (downward)" />
            <h4>0xa1 Green Piranha Plant (downward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x3e, 0x3f, 0x111, 0x112</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a2-red-piranha-plant-upward.png" alt="Sprite preview for enemy ID 0xa2, Red Piranha Plant (upward)" />
            <h4>0xa2 Red Piranha Plant (upward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x10d, 0x10e, 0x02, 0x03</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a3-red-piranha-plant-downward.png" alt="Sprite preview for enemy ID 0xa3, Red Piranha Plant (downward)" />
            <h4>0xa3 Red Piranha Plant (downward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x3e, 0x3f, 0x10f, 0x110</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a4-green-venus-fire-trap-upward.png" alt="Sprite preview for enemy ID 0xa4, Green Venus Fire Trap (upward)" />
            <h4>0xa4 Green Venus Fire Trap (upward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x107, 0x108, 0x02, 0x03</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a5-green-venus-fire-trap-downward.png" alt="Sprite preview for enemy ID 0xa5, Green Venus Fire Trap (downward)" />
            <h4>0xa5 Green Venus Fire Trap (downward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x3e, 0x3f, 0x113, 0x114</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a6-red-venus-fire-trap-upward.png" alt="Sprite preview for enemy ID 0xa6, Red Venus Fire Trap (upward)" />
            <h4>0xa6 Red Venus Fire Trap (upward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x109, 0x10a, 0x02, 0x03</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-a7-red-venus-fire-trap-downward.png" alt="Sprite preview for enemy ID 0xa7, Red Venus Fire Trap (downward)" />
            <h4>0xa7 Red Venus Fire Trap (downward)</h4>
            <p><strong>Size:</strong> 2x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0x3e, 0x3f, 0x115, 0x116</p>
            <p><strong>Notes:</strong> none</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-unknown-and-placeholder-entries">
        <h3>Unknown and Placeholder Entries</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-00-msg-nothing.png" alt="Sprite preview for enemy ID 0x00, MSG_NOTHING" />
            <h4>0x00 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-01-weird-thing-can-slip-on.png" alt="Sprite preview for enemy ID 0x01, Weird thing, can slip on" />
            <h4>0x01 Weird thing, can slip on</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-03-msg-nothing.png" alt="Sprite preview for enemy ID 0x03, MSG_NOTHING" />
            <h4>0x03 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-04-weird-enemy.png" alt="Sprite preview for enemy ID 0x04, Weird enemy" />
            <h4>0x04 Weird enemy</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-05-weird-enemy.png" alt="Sprite preview for enemy ID 0x05, Weird enemy" />
            <h4>0x05 Weird enemy</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-0a-weird-enemy.png" alt="Sprite preview for enemy ID 0x0a, Weird enemy" />
            <h4>0x0a Weird enemy</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-0f-msg-nothing.png" alt="Sprite preview for enemy ID 0x0f, MSG_NOTHING" />
            <h4>0x0f MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-10-msg-nothing.png" alt="Sprite preview for enemy ID 0x10, MSG_NOTHING" />
            <h4>0x10 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-11-msg-nothing.png" alt="Sprite preview for enemy ID 0x11, MSG_NOTHING" />
            <h4>0x11 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-12-msg-nothing.png" alt="Sprite preview for enemy ID 0x12, MSG_NOTHING" />
            <h4>0x12 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-13-msg-nothing.png" alt="Sprite preview for enemy ID 0x13, MSG_NOTHING" />
            <h4>0x13 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-14-msg-nothing.png" alt="Sprite preview for enemy ID 0x14, MSG_NOTHING" />
            <h4>0x14 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-15-msg-nothing.png" alt="Sprite preview for enemy ID 0x15, MSG_NOTHING" />
            <h4>0x15 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-16-msg-nothing.png" alt="Sprite preview for enemy ID 0x16, MSG_NOTHING" />
            <h4>0x16 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-1a-weird.png" alt="Sprite preview for enemy ID 0x1a, Weird" />
            <h4>0x1a Weird</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-1d-msg-nothing.png" alt="Sprite preview for enemy ID 0x1d, MSG_NOTHING" />
            <h4>0x1d MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-20-msg-nothing.png" alt="Sprite preview for enemy ID 0x20, MSG_NOTHING" />
            <h4>0x20 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-47-msg-nothing.png" alt="Sprite preview for enemy ID 0x47, MSG_NOTHING" />
            <h4>0x47 MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-4d-msg-nothing.png" alt="Sprite preview for enemy ID 0x4d, MSG_NOTHING" />
            <h4>0x4d MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-4e-msg-nothing.png" alt="Sprite preview for enemy ID 0x4e, MSG_NOTHING" />
            <h4>0x4e MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-54-weird-block.png" alt="Sprite preview for enemy ID 0x54, Weird Block" />
            <h4>0x54 Weird Block</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-9b-msg-nothing.png" alt="Sprite preview for enemy ID 0x9b, MSG_NOTHING" />
            <h4>0x9b MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-9c-msg-nothing.png" alt="Sprite preview for enemy ID 0x9c, MSG_NOTHING" />
            <h4>0x9c MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ab-msg-nothing.png" alt="Sprite preview for enemy ID 0xab, MSG_NOTHING" />
            <h4>0xab MSG_NOTHING</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x92</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b3-weird-flashing-enemy.png" alt="Sprite preview for enemy ID 0xb3, Weird flashing enemy" />
            <h4>0xb3 Weird flashing enemy</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-crash-entries">
        <h3>Crash Entries</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d7-msg-crash.png" alt="Sprite preview for enemy ID 0xd7, MSG_CRASH" />
            <h4>0xd7 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d8-msg-crash.png" alt="Sprite preview for enemy ID 0xd8, MSG_CRASH" />
            <h4>0xd8 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d9-msg-crash.png" alt="Sprite preview for enemy ID 0xd9, MSG_CRASH" />
            <h4>0xd9 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-da-msg-crash.png" alt="Sprite preview for enemy ID 0xda, MSG_CRASH" />
            <h4>0xda MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-db-msg-crash.png" alt="Sprite preview for enemy ID 0xdb, MSG_CRASH" />
            <h4>0xdb MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-dc-msg-crash.png" alt="Sprite preview for enemy ID 0xdc, MSG_CRASH" />
            <h4>0xdc MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-dd-msg-crash.png" alt="Sprite preview for enemy ID 0xdd, MSG_CRASH" />
            <h4>0xdd MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-de-msg-crash.png" alt="Sprite preview for enemy ID 0xde, MSG_CRASH" />
            <h4>0xde MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-df-msg-crash.png" alt="Sprite preview for enemy ID 0xdf, MSG_CRASH" />
            <h4>0xdf MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e0-msg-crash.png" alt="Sprite preview for enemy ID 0xe0, MSG_CRASH" />
            <h4>0xe0 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e1-msg-crash.png" alt="Sprite preview for enemy ID 0xe1, MSG_CRASH" />
            <h4>0xe1 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e2-msg-crash.png" alt="Sprite preview for enemy ID 0xe2, MSG_CRASH" />
            <h4>0xe2 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e3-msg-crash.png" alt="Sprite preview for enemy ID 0xe3, MSG_CRASH" />
            <h4>0xe3 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e4-msg-crash.png" alt="Sprite preview for enemy ID 0xe4, MSG_CRASH" />
            <h4>0xe4 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e5-msg-crash.png" alt="Sprite preview for enemy ID 0xe5, MSG_CRASH" />
            <h4>0xe5 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e6-msg-crash.png" alt="Sprite preview for enemy ID 0xe6, MSG_CRASH" />
            <h4>0xe6 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e7-msg-crash.png" alt="Sprite preview for enemy ID 0xe7, MSG_CRASH" />
            <h4>0xe7 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e8-msg-crash.png" alt="Sprite preview for enemy ID 0xe8, MSG_CRASH" />
            <h4>0xe8 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-e9-msg-crash.png" alt="Sprite preview for enemy ID 0xe9, MSG_CRASH" />
            <h4>0xe9 MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ea-msg-crash.png" alt="Sprite preview for enemy ID 0xea, MSG_CRASH" />
            <h4>0xea MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-eb-msg-crash.png" alt="Sprite preview for enemy ID 0xeb, MSG_CRASH" />
            <h4>0xeb MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ec-msg-crash.png" alt="Sprite preview for enemy ID 0xec, MSG_CRASH" />
            <h4>0xec MSG_CRASH</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x91</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
        </div>
      </section>
      <section class="enemy-catalog-category" id="enemy-category-other-entries">
        <h3>Other Entries</h3>
        <div class="enemy-card-grid">
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-02-makes-you-bounce-at-beginning-of-level.png" alt="Sprite preview for enemy ID 0x02, Makes you bounce at beginning of level" />
            <h4>0x02 Makes you bounce at beginning of level</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-2a-ptooie.png" alt="Sprite preview for enemy ID 0x2a, Ptooie" />
            <h4>0x2a Ptooie</h4>
            <p><strong>Size:</strong> 1x2 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 7</p>
            <p><strong>Blocks:</strong> 0x32, 0x42</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-2f-boo-diddley.png" alt="Sprite preview for enemy ID 0x2f, Boo Diddley" />
            <h4>0x2f Boo Diddley</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x29</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-30-hot-foot.png" alt="Sprite preview for enemy ID 0x30, Hot Foot" />
            <h4>0x30 Hot Foot</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x58</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-31-top-stretch.png" alt="Sprite preview for enemy ID 0x31, Top Stretch" />
            <h4>0x31 Top Stretch</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x2d</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-32-bottom-stretch.png" alt="Sprite preview for enemy ID 0x32, Bottom Stretch" />
            <h4>0x32 Bottom Stretch</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 3</p>
            <p><strong>Blocks:</strong> 0x2e</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-34-toad-message.png" alt="Sprite preview for enemy ID 0x34, Toad &amp; Message" />
            <h4>0x34 Toad &amp; Message</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-35-automatically-clear-stage.png" alt="Sprite preview for enemy ID 0x35, Automatically Clear Stage" />
            <h4>0x35 Automatically Clear Stage</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-45-smart-hot-foot.png" alt="Sprite preview for enemy ID 0x45, Smart Hot Foot" />
            <h4>0x45 Smart Hot Foot</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x58</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-49-background-cloud.png" alt="Sprite preview for enemy ID 0x49, Background Cloud" />
            <h4>0x49 Background Cloud</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x5c, 0x5d</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-4a-magic-ball.png" alt="Sprite preview for enemy ID 0x4a, Magic Ball" />
            <h4>0x4a Magic Ball</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x5e</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-5c-instantly-broken-brick.png" alt="Sprite preview for enemy ID 0x5c, Instantly broken brick" />
            <h4>0x5c Instantly broken brick</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-65-upward-current.png" alt="Sprite preview for enemy ID 0x65, Upward Current" />
            <h4>0x65 Upward Current</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x81</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-66-downward-current.png" alt="Sprite preview for enemy ID 0x66, Downward Current" />
            <h4>0x66 Downward Current</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x82</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ad-brown-rocky-wrench.png" alt="Sprite preview for enemy ID 0xad, Brown Rocky Wrench" />
            <h4>0xad Brown Rocky Wrench</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x1b</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-ae-nut-use-with-corkscrew.png" alt="Sprite preview for enemy ID 0xae, Nut (use with corkscrew)" />
            <h4>0xae Nut (use with corkscrew)</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x55, 0x56</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-b8-moving-background-clouds.png" alt="Sprite preview for enemy ID 0xb8, Moving Background Clouds" />
            <h4>0xb8 Moving Background Clouds</h4>
            <p><strong>Size:</strong> 2x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x5c, 0x5d</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-bd-missile-bills.png" alt="Sprite preview for enemy ID 0xbd, Missile Bills" />
            <h4>0xbd Missile Bills</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 1 / group 3</p>
            <p><strong>Blocks:</strong> 0xa7</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-be-rocky-wrench.png" alt="Sprite preview for enemy ID 0xbe, Rocky Wrench" />
            <h4>0xbe Rocky Wrench</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> clan 2 / group 5</p>
            <p><strong>Blocks:</strong> 0x12</p>
            <p><strong>Notes:</strong> none</p>
          </article>
          <article class="enemy-card">
            <img src="../_static/images/enemy_catalog/entries/enemy-d5-the-king-has-been-transformed-message.png" alt="Sprite preview for enemy ID 0xd5, &#x27;The king has been transformed&#x27; message" />
            <h4>0xd5 &#x27;The king has been transformed&#x27; message</h4>
            <p><strong>Size:</strong> 1x1 blocks</p>
            <p><strong>Clan/group:</strong> unmatched</p>
            <p><strong>Blocks:</strong> 0x94</p>
            <p><strong>Notes:</strong> no-clan-group-match</p>
          </article>
        </div>
      </section>
   </div>
