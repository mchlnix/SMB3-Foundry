import tempfile

from foundry.game.File import ROM
from smb3parse.util.parser import FoundLevel


def test_load_additional_data_from_rom(rom):
    assert not rom.additional_data

    rom.additional_data.managed_level_positions = True
    rom.additional_data.found_level_information.append(FoundLevel([1], [2], 3, 4, 5, 6, 7, 8, True, True, True))

    assert rom.additional_data

    old_rom_path = ROM.path

    with tempfile.NamedTemporaryFile("r+b") as temp:
        rom.save_to_file(temp.name)

        ROM.load_from_file(temp.name)

    ROM.path = old_rom_path

    assert rom.additional_data
