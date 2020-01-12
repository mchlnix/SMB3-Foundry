import pytest

from foundry.gui.BlockViewer import BlockViewer


@pytest.fixture
def block_viewer(qtbot):
    block_viewer = BlockViewer(None)

    block_viewer.show()

    qtbot.addWidget(block_viewer)

    return block_viewer


def test_prev_object_set(block_viewer, qtbot):
    # GIVEN the block viewer at a specific object set, which is not the first
    block_viewer.next_os_action.trigger()

    current_object_set = block_viewer.bank_dropdown.currentIndex()
    first_object_set = 0

    assert current_object_set != first_object_set

    current_blocks_shown = block_viewer.sprite_bank.grab().toImage()
    assert current_blocks_shown == block_viewer.sprite_bank.grab().toImage()

    # WHEN the next object set action is triggered
    block_viewer.prev_os_action.trigger()

    # THEN the dropdown is updated and a different graphic is shown
    assert block_viewer.bank_dropdown.currentIndex() == current_object_set - 1
    assert block_viewer.sprite_bank.grab() != current_blocks_shown


def test_next_object_set(block_viewer, qtbot):
    # GIVEN the block viewer at a specific object set, which is not the last
    current_object_set = block_viewer.bank_dropdown.currentIndex()
    last_object_set = block_viewer.bank_dropdown.count() - 1

    assert current_object_set != last_object_set

    current_blocks_shown = block_viewer.sprite_bank.grab().toImage()
    assert current_blocks_shown == block_viewer.sprite_bank.grab().toImage()

    # WHEN the next object set action is triggered
    block_viewer.next_os_action.trigger()

    # THEN the dropdown is updated and a different graphic is shown
    assert block_viewer.bank_dropdown.currentIndex() == current_object_set + 1
    assert block_viewer.sprite_bank.grab() != current_blocks_shown


def test_zoom_out(block_viewer, qtbot):
    # GIVEN the block viewer at the default zoom level
    current_zoom_level = block_viewer.sprite_bank.size().height() / block_viewer.sprite_bank.zoom_step

    # WHEN the zoom out action is called
    block_viewer.zoom_out_action.trigger()

    # THEN the new zoom level is 1 lower and the size of the bank is accordingly smaller
    new_zoom_level = block_viewer.sprite_bank.size().height() / block_viewer.sprite_bank.zoom_step

    assert new_zoom_level == current_zoom_level - 1


def test_zoom_in(block_viewer, qtbot):
    # GIVEN the block viewer at the default zoom level
    current_zoom_level = block_viewer.sprite_bank.size().height() / block_viewer.sprite_bank.zoom_step

    # WHEN the zoom in action is called
    block_viewer.zoom_in_action.trigger()

    # THEN the new zoom level is 1 higher and the size of the bank is accordingly larger
    new_zoom_level = block_viewer.sprite_bank.size().height() / block_viewer.sprite_bank.zoom_step

    assert new_zoom_level == current_zoom_level + 1
