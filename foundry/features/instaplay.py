from foundry.game.level.Level import Level
from foundry.gui.dialogs.SettingsDialog import PowerupEntry
from smb3parse.constants import (
    BASE_OFFSET,
    PAGE_A000_OFFSET,
    POWERUP_ADDITION_PWING,
    POWERUP_ADDITION_STARMAN,
    STARTING_WORLD_INDEX_ADDRESS,
    TILE_LEVEL_1,
    Title_DebugMenu,
    Title_PrepForWorldMap,
)
from smb3parse.levels import WORLD_COUNT
from smb3parse.levels.world_map import WorldMap
from smb3parse.util import JSR, LDA_CONST, LDY_CONST, NOP, RTS, STA_OFFSET, STY_RAM
from smb3parse.util.rom import PRG_BANK_SIZE, Rom


class CantFindFirstTile(LookupError):
    def __init__(self, world: int):
        self.world = world

        super().__init__()


class LevelNotAttached(ValueError):
    pass


class InstaPlayer:
    def __init__(self, rom: Rom):
        self.rom = rom

    def set_default_powerup(self, powerup: PowerupEntry, with_starman=False):
        # RAM values need to be set via code during run time
        ram_map_power_starman = 0x03F2
        ram_map_power_disp = 0x03F3

        # set default powerup when starting a world
        self.rom.write(Title_PrepForWorldMap + 0x1, bytes([powerup.power_up_code]))

        if not powerup.has_p_wing or with_starman:
            return

        # If a P-wing powerup or starman is selected, another variable needs to be set with the P-wing/Star Man value
        debug_bytes = bytearray()

        if with_starman:
            debug_bytes.extend(_set_ram_value(POWERUP_ADDITION_STARMAN, ram_map_power_starman))

        if powerup.has_p_wing:
            debug_bytes.extend(_set_ram_value(POWERUP_ADDITION_PWING, ram_address=ram_map_power_disp))

            # Remove code that resets the powerup value by replacing it with no-operations
            # Otherwise this code would copy the value of the normal powerup here
            # (So if the powerup would be Raccoon Mario, Map_Power_Disp would also be
            # set as Raccoon Mario instead of P-wing
            map_power_disp_reset_address = 0x3C5A2
            self.rom.write(map_power_disp_reset_address, bytes([NOP] * 3))

        # add rts, to jump back out of the debug menu
        debug_bytes.append(RTS)

        # We need to start one byte before Title_DebugMenu to remove the RTS of Title_PrepForWorldMap
        # The assembly code below reads as follows:
        self.rom.write(Title_DebugMenu - 0x1, debug_bytes)

    def put_current_level_to_level_1_1(self, level: Level) -> bool:
        if not level.attached_to_rom:
            raise LevelNotAttached

        world = level.world

        if world not in range(1, WORLD_COUNT):
            world = 1

        world_map = WorldMap.from_world_number(self.rom, world)

        # find position of "level 1" tile in world map
        for position in world_map.gen_positions():
            if position.tile() == TILE_LEVEL_1:
                break
        else:
            raise CantFindFirstTile(world)

        # write level and enemy data of current level
        (layout_address, layout_bytes), (enemy_address, enemy_bytes) = level.to_bytes()
        self.rom.write(layout_address, layout_bytes)
        self.rom.write(enemy_address, enemy_bytes)

        # replace level information with that of current level
        object_set_number = level.object_set_number

        world_map.replace_level_at_position((layout_address, enemy_address, object_set_number), position)

        # replace the world the game loads into after the title screen
        self.rom.write(STARTING_WORLD_INDEX_ADDRESS, world - 1)

        return True

    def skip_title_screen(self):
        # skip rendering the title screen by jumping to the code after selecting player count (1P or 2P)
        prg_24_offset = BASE_OFFSET + 24 * PRG_BANK_SIZE - PAGE_A000_OFFSET

        after_player_init = prg_24_offset + 0xA8FC
        title_screen_state_injection_rel = 0xACAE

        self.rom.write(after_player_init, JSR)
        self.rom.write_little_endian(after_player_init + 1, title_screen_state_injection_rel)

        title_screen_state_injection_abs = prg_24_offset + title_screen_state_injection_rel
        title_screen_state_after_player_selection = 0x04
        ram_title_screen_address = 0xDE

        self.rom.write(title_screen_state_injection_abs, LDY_CONST)
        self.rom.write(title_screen_state_injection_abs + 1, title_screen_state_after_player_selection)
        self.rom.write(title_screen_state_injection_abs + 2, STY_RAM)
        self.rom.write(title_screen_state_injection_abs + 3, ram_title_screen_address)


def _set_ram_value(value: int, ram_address) -> bytearray:
    return_bytes = bytearray()

    return_bytes.extend([LDA_CONST, value])

    addr_hi = ram_address >> 8
    addr_lo = ram_address % 2**8

    return_bytes.extend([STA_OFFSET, addr_lo, addr_hi])

    return return_bytes
