from foundry.game.gfx.Palette import PaletteGroup, load_palette_group, restore_all_palettes


def test_restore_palettes():
    # GIVEN a PaletteGroup object
    example_palette_group = load_palette_group(1, 1)

    # WHEN one of the palettes is changed and marked as such, then restored
    old_palette = example_palette_group.palettes[0].copy()
    assert example_palette_group.palettes[0] == old_palette

    example_palette_group.palettes[0][0] += 1
    PaletteGroup.changed = True

    assert example_palette_group.palettes[0] != old_palette

    restore_all_palettes()

    # THEN the palette should be restored correctly and they are not marked as changed anymore
    assert example_palette_group.palettes[0] == old_palette
    assert not PaletteGroup.changed
