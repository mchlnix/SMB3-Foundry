from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Union

from PySide6.QtWidgets import QFileDialog, QMessageBox

from foundry import ASM_FILE_FILTER
from foundry.gui.ObjectSetSelector import ObjectSetSelector

if TYPE_CHECKING:
    from foundry.game.level.Level import Level


def asm_to_bytes(asm: str) -> bytearray:
    ret = bytearray()

    for line in asm.split("\n"):
        before_comment, *_after_comment = line.split(";")

        if not (stripped_line := before_comment.strip()):
            # no code before comment, ignore line
            continue

        if ".word" in stripped_line:
            QMessageBox.warning(
                None,
                "Parsing Error",
                f"Cannot parse '{stripped_line}'. Probably an unknown offset, you'll have to set in the level header. "
                f"Using 0x0000 as value for now.",
            )
            bytes_in_line = bytearray(2)

        elif ".byte" not in stripped_line:
            # no comment, no word, no byte = ???
            continue

        elif "|" in stripped_line:
            # lines full of macros
            bytes_in_line = bytearray([_parse_macros_in_line(stripped_line)])

        else:
            bytes_in_line = [int(byte, 16) for byte in stripped_line.replace(", ", "").split("$")[1:]]

        ret.extend(bytes_in_line)

    ret.append(0xFF)

    return ret


def _parse_macros_in_line(line: str) -> int:
    line = line.removeprefix(".byte ")

    byte = 0

    for macro in map(str.strip, line.split("|")):
        if macro in MACRO_DICT:
            byte += MACRO_DICT[macro]
        else:
            raise ValueError(f"Can't determine value for '{macro}'. Maybe a typo?")

    return byte


def bytes_to_asm(data: Union[bytearray, int]) -> str:
    if isinstance(data, int):
        hex_data = f"${data:02X}"
    else:
        assert isinstance(data, bytearray)
        hex_data = ", ".join([f"${byte:02X}" for byte in data])

    return hex_data.replace("0x", "$").upper()


def load_asm_filename(what: str, default_path=""):
    pathname, _ = QFileDialog.getOpenFileName(
        None, caption=f"Open {what} file", dir=default_path, filter=ASM_FILE_FILTER
    )

    return pathname


def save_asm_filename(what: str, default_path=""):
    pathname, _ = QFileDialog.getSaveFileName(
        None,
        caption=f"Save {what} as",
        dir=default_path,
        filter=ASM_FILE_FILTER,
    )

    return pathname


def load_asm_level(pathname: PathLike, level: "Level"):
    try:
        with open(pathname, "r") as asm_file:
            asm_level_data = asm_file.read()
    except IOError as exp:
        QMessageBox.critical(None, type(exp).__name__, f"Cannot open file '{pathname}'.")
        return

    object_set = ObjectSetSelector.get_object_set()

    if object_set == -1:
        # was cancelled
        return

    try:
        level.from_asm(object_set, asm_to_bytes(asm_level_data))
    except ValueError as ve:
        QMessageBox.critical(None, type(ve).__name__, str(ve))
        return

    level.name = Path(pathname).stem


def load_asm_enemy(pathname: PathLike, level: "Level"):
    try:
        with open(pathname, "r") as asm_file:
            asm_enemy_data = asm_file.read()
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Cannot open file '{pathname}'.")
        return

    _, (__, current_enemy_bytes) = level.to_bytes()

    level._load_enemies(current_enemy_bytes[:-1] + asm_to_bytes(asm_enemy_data)[1:])

    level.data_changed.emit()


def save_asm(what: str, pathname: PathLike, asm_data: str):
    try:
        with open(pathname, "w") as asm_file:
            asm_file.write(asm_data)
    except IOError as exp:
        QMessageBox.warning(None, type(exp).__name__, f"Couldn't save {what} to '{pathname}'.")


# taken from https://github.com/captainsouthbird/smb3/blob/b900ac59622f58a2266b30a32acc700e89415e83/smb3.asm#L3025
MACRO_DICT = {
    # Size of level (width or height, if vertical)
    "LEVEL1_SIZE_01": 0b00000000,
    "LEVEL1_SIZE_02": 0b00000001,
    "LEVEL1_SIZE_03": 0b00000010,
    "LEVEL1_SIZE_04": 0b00000011,
    "LEVEL1_SIZE_05": 0b00000100,
    "LEVEL1_SIZE_06": 0b00000101,
    "LEVEL1_SIZE_07": 0b00000110,
    "LEVEL1_SIZE_08": 0b00000111,
    "LEVEL1_SIZE_09": 0b00001000,
    "LEVEL1_SIZE_10": 0b00001001,
    "LEVEL1_SIZE_11": 0b00001010,
    "LEVEL1_SIZE_12": 0b00001011,
    "LEVEL1_SIZE_13": 0b00001100,
    "LEVEL1_SIZE_14": 0b00001101,
    "LEVEL1_SIZE_15": 0b00001110,
    "LEVEL1_SIZE_16": 0b00001111,
    # Player Y Start positions (also selects appropriate starting vertical position)
    "LEVEL1_YSTART_170": 0b00000000,
    "LEVEL1_YSTART_040": 0b00100000,
    "LEVEL1_YSTART_000": 0b01000000,
    "LEVEL1_YSTART_140": 0b01100000,
    "LEVEL1_YSTART_070": 0b10000000,
    "LEVEL1_YSTART_0B0": 0b10100000,
    "LEVEL1_YSTART_0F0": 0b11000000,
    "LEVEL1_YSTART_180": 0b11100000,
    "LEVEL1_2PVS": 0b00010000,  # Unknown purpose flag set on 2P Vs levels
    # Palettes (full 16 colors in category) are defined by tileset# objects are rooted at index 8
    # "BG palette set
    "LEVEL2_BGPAL_00": 0b00000000,
    "LEVEL2_BGPAL_01": 0b00000001,
    "LEVEL2_BGPAL_02": 0b00000010,
    "LEVEL2_BGPAL_03": 0b00000011,
    "LEVEL2_BGPAL_04": 0b00000100,
    "LEVEL2_BGPAL_05": 0b00000101,
    "LEVEL2_BGPAL_06": 0b00000110,
    "LEVEL2_BGPAL_07": 0b00000111,
    # Object palette set
    "LEVEL2_OBJPAL_08": 0b00000000,
    "LEVEL2_OBJPAL_09": 0b00001000,
    "LEVEL2_OBJPAL_10": 0b00010000,
    "LEVEL2_OBJPAL_11": 0b00011000,
    # Player X Start positions
    "LEVEL2_XSTART_18": 0b00000000,
    "LEVEL2_XSTART_70": 0b00100000,
    "LEVEL2_XSTART_D8": 0b01000000,
    "LEVEL2_XSTART_80": 0b01100000,
    # Sets "Level_UnusedFlag", which is apparently not used for anything
    "LEVEL2_UNUSEDFLAG": 0b10000000,
    # "Sets "Level_AltTileset", the tileset of the "alternate" level
    "LEVEL3_TILESET_00": 0b00000000,  # Included for completeness, but not valid (for the world map only)
    "LEVEL3_TILESET_01": 0b00000001,
    "LEVEL3_TILESET_02": 0b00000010,
    "LEVEL3_TILESET_03": 0b00000011,
    "LEVEL3_TILESET_04": 0b00000100,
    "LEVEL3_TILESET_05": 0b00000101,
    "LEVEL3_TILESET_06": 0b00000110,
    "LEVEL3_TILESET_07": 0b00000111,
    "LEVEL3_TILESET_08": 0b00001000,
    "LEVEL3_TILESET_09": 0b00001001,
    "LEVEL3_TILESET_10": 0b00001010,
    "LEVEL3_TILESET_11": 0b00001011,
    "LEVEL3_TILESET_12": 0b00001100,
    "LEVEL3_TILESET_13": 0b00001101,
    "LEVEL3_TILESET_14": 0b00001110,
    "LEVEL3_TILESET_15": 0b00001111,  # Included for completeness, but not valid (bonus game, can't jump in this way)
    # Sets "Level_7Vertical", i.e. states object is a vertical oriented one
    "LEVEL3_VERTICAL": 0b00010000,
    # "Sets the vertical scroll lock
    "LEVEL3_VSCROLL_LOCKLOW": 0b00000000,  # Screen locked at $EF (lowest point) unless flying or climbing a vine
    "LEVEL3_VSCROLL_FREE": 0b00100000,  # Free vertical scroll
    "LEVEL3_VSCROLL_LOCKED": 0b01000000,  # Locks either high (0) or low ($EF) depending on value of Vert_Scroll
    # Sets Level_PipeNotExit
    "LEVEL3_PIPENOTEXIT": 0b10000000,
    # graphics set
    "LEVEL4_BGBANK_INDEX(0)": 0,
    "LEVEL4_BGBANK_INDEX(1)": 1,
    "LEVEL4_BGBANK_INDEX(2)": 2,
    "LEVEL4_BGBANK_INDEX(3)": 3,
    "LEVEL4_BGBANK_INDEX(4)": 4,
    "LEVEL4_BGBANK_INDEX(5)": 5,
    "LEVEL4_BGBANK_INDEX(6)": 6,
    "LEVEL4_BGBANK_INDEX(7)": 7,
    "LEVEL4_BGBANK_INDEX(8)": 8,
    "LEVEL4_BGBANK_INDEX(9)": 9,
    "LEVEL4_BGBANK_INDEX(10)": 10,
    "LEVEL4_BGBANK_INDEX(11)": 11,
    "LEVEL4_BGBANK_INDEX(12)": 12,
    "LEVEL4_BGBANK_INDEX(13)": 13,
    "LEVEL4_BGBANK_INDEX(14)": 14,
    "LEVEL4_BGBANK_INDEX(15)": 15,
    "LEVEL4_BGBANK_INDEX(16)": 16,
    "LEVEL4_BGBANK_INDEX(17)": 17,
    "LEVEL4_BGBANK_INDEX(18)": 18,
    "LEVEL4_BGBANK_INDEX(19)": 19,
    "LEVEL4_BGBANK_INDEX(20)": 20,
    "LEVEL4_BGBANK_INDEX(21)": 21,
    "LEVEL4_BGBANK_INDEX(22)": 22,
    "LEVEL4_BGBANK_INDEX(23)": 23,
    "LEVEL4_BGBANK_INDEX(24)": 24,
    "LEVEL4_BGBANK_INDEX(25)": 25,
    "LEVEL4_BGBANK_INDEX(26)": 26,
    "LEVEL4_BGBANK_INDEX(27)": 27,
    "LEVEL4_BGBANK_INDEX(28)": 28,
    "LEVEL4_BGBANK_INDEX(29)": 29,
    "LEVEL4_BGBANK_INDEX(30)": 30,
    "LEVEL4_BGBANK_INDEX(31)": 31,
    # Level initial action
    "LEVEL4_INITACT_NOTHING": 0b00000000,  # Do nothing
    "LEVEL4_INITACT_SLIDE": 0b00100000,  # Start level sliding (if able by power-up)
    "LEVEL4_INITACT_PIPE_T": 0b01000000,  # Start by exiting top of pipe
    "LEVEL4_INITACT_PIPE_B": 0b01100000,  # Start by exiting bottom of pipe
    "LEVEL4_INITACT_PIPE_R": 0b10000000,  # Start by exiting right of pipe
    "LEVEL4_INITACT_PIPE_L": 0b10100000,  # Start by exiting left of pipe
    "LEVEL4_INITACT_AIRSHIP": 0b11000000,  # Airship intro run & jump init
    "LEVEL4_INITACT_AIRSHIPB": 0b11100000,  # Boarding the Airship
    # Select "Music 2" set BGM (from table GamePlay_BGM)
    "LEVEL5_BGM_OVERWORLD": 0b00000000,
    "LEVEL5_BGM_UNDERGROUND": 0b00000001,
    "LEVEL5_BGM_UNDERWATER": 0b00000010,
    "LEVEL5_BGM_FORTRESS": 0b00000011,
    "LEVEL5_BGM_BOSS": 0b00000100,
    "LEVEL5_BGM_AIRSHIP": 0b00000101,
    "LEVEL5_BGM_BATTLE": 0b00000110,
    "LEVEL5_BGM_TOADHOUSE": 0b00000111,
    "LEVEL5_BGM_ATHLETIC": 0b00001000,
    "LEVEL5_BGM_THRONEROOM": 0b00001001,
    "LEVEL5_BGM_SKY": 0b00001010,
    # Bits 4-5 are free apparently
    # Set starting clock time
    "LEVEL5_TIME_300": 0b00000000,  # Clock at 300,
    "LEVEL5_TIME_400": 0b01000000,  # Clock at 400,
    "LEVEL5_TIME_200": 0b10000000,  # Clock at 200,
    "LEVEL5_TIME_UNLIMITED": 0b11000000,  # Clock at 000, unlimited
}
