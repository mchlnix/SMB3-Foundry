import os

import pytest
from PySide2.QtGui import QPixmap

from approval_tests.gui import ApprovalDialog
from foundry import root_dir
from foundry.game.File import ROM

level_1_1_object_address = 0x1FB92
level_1_1_enemy_address = 0xC537 + 1

level_1_2_object_address = 0x20F3A
level_1_2_enemy_address = 0xC6BA + 1


@pytest.fixture(scope="module", autouse=True)
def rom():
    rom_path = root_dir.joinpath("SMB3.nes")

    rom = ROM(rom_path)

    yield rom


def compare_images(image_name: str, ref_image_path: str, gen_image: QPixmap):
    if os.path.exists(ref_image_path):
        result = ApprovalDialog.compare(image_name, QPixmap(ref_image_path), gen_image)

        if result == ApprovalDialog.Rejected:
            pytest.fail(f"{image_name} did not look like the reference.")
        elif result == ApprovalDialog.Accepted:
            pass
        elif result == ApprovalDialog.Ignore:
            pytest.skip(f"{image_name} did not look like the reference, but was ignored.")
        else:
            # accepted and overwrite ref
            gen_image.toImage().save(ref_image_path)

            pass
    else:
        gen_image.toImage().save(ref_image_path)

        pytest.skip(f"No ref image was found. Saved new ref under {ref_image_path}.")
