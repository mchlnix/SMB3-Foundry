"""Patch a temporary ROM so the active level can be launched quickly.

This module sits between the editor's save pipeline and emulator launch flow.
``FoundryMainWindow`` creates a disposable ROM copy, ``InstaPlayer`` rewrites
startup and world-map bytes in that copy, and the configured emulator then
boots through enough normal SMB3 flow to enter the edited level without
touching the user's source ROM.

See Also
--------
foundry.gui.FoundryMainWindow
    Stages the temporary ROM copy and delegates patching to ``InstaPlayer``.
foundry.gui.dialogs.SettingsDialog
    Stores the emulator command and default instaplay power-up choices that
    control these patches.
foundry.features.rom_reload
    Handles the complementary workflow of detecting ROM changes after external
    tools, such as an emulator, have run.
"""

from foundry.game.level.Level import Level
from foundry.gui.dialogs.SettingsDialog import PowerupEntry
from smb3parse.constants import (
    BASE_OFFSET,
    PAGE_A000_OFFSET,
    POWERUP_ADDITION_PWING,
    POWERUP_ADDITION_STARMAN,
    STARTING_WORLD_INDEX_ADDRESS,
    TILE_LEVEL_1,
    Constants,
)
from smb3parse.levels import WORLD_COUNT
from smb3parse.levels.world_map import WorldMap
from smb3parse.util import JSR, LDA_CONST, LDY_CONST, NOP, RTS, STA_OFFSET, STY_RAM
from smb3parse.util.rom import PRG_BANK_SIZE, Rom


class CantFindFirstTile(LookupError):
    """Raised when a world map has no level-1 tile for instaplay.

    Instaplay redirects the first level tile in the active world to the edited
    level. Without that tile there is no stable map position to patch.

    Parameters
    ----------
    world : int
        World map or world number being processed.

    Attributes
    ----------
    world : int
        One-based world number that could not be patched.

    Notes
    -----
    Instaplay needs a stable world-map entry point so the game can enter the
    edited level through normal SMB3 map logic. This error means the selected
    world map did not expose the expected level-1 tile.

    See Also
    --------
    InstaPlayer.put_current_level_to_level_1_1
        Performs the world-map redirect that may raise this error.
    """

    def __init__(self, world: int):
        """Store the world number that could not be patched.

        Parameters
        ----------
        world : int
            World map or world number being processed.
        """
        self.world = world

        super().__init__()


class LevelNotAttached(ValueError):
    """Raised when instaplay needs ROM addresses for a detached level.

    Instaplay writes the edited level back into a temporary ROM copy before
    launching the emulator. Detached levels do not yet have stable object and
    enemy data addresses, so there is nowhere to write that data.

    See Also
    --------
    InstaPlayer.put_current_level_to_level_1_1
        Raises the error when the selected level is not attached to ROM data.
    """

    pass


class InstaPlayer:
    """Patch ROM bytes for fast emulator testing.

    The class operates on a caller-provided ROM instance, usually a temporary
    copy created by the main window. Its methods patch SMB3 startup flow,
    default player power-up state, and world-map level metadata so the emulator
    can reach the edited level with minimal menu navigation.

    Parameters
    ----------
    rom : Rom
        ROM data source used for game data lookups.

    Attributes
    ----------
    rom : Rom
        ROM copy being patched for emulator launch.

    Examples
    --------
    ``InstaPlayer`` is normally driven by ``FoundryMainWindow`` after the
    editor has written the active level into a disposable ROM copy. The patch
    order mirrors that launch workflow: configure the startup state, redirect
    world-map entry to the edited level, then remove front-end delays.

    >>> from types import SimpleNamespace
    >>> temp_rom = Rom(bytearray(0x40000))
    >>> player = InstaPlayer(temp_rom)
    >>> powerup = PowerupEntry("Big Mario", 6, 48, 1, False)
    >>> editor_level = SimpleNamespace(
    ...     attached_to_rom=True,
    ...     world=1,
    ...     object_set_number=3,
    ...     to_bytes=lambda: (
    ...         (0x1F000, bytearray(b"LEVEL")),
    ...         (0x1F200, bytearray(b"ENEMY")),
    ...     ),
    ... )
    >>> layout, enemy = editor_level.to_bytes()
    >>> layout[0], bytes(layout[1]), enemy[0], bytes(enemy[1])
    (126976, b'LEVEL', 127488, b'ENEMY')

    In production, ``put_current_level_to_level_1_1`` consumes a real
    :class:`~foundry.game.level.Level.Level` instance with the same attached
    state and ``to_bytes`` result shape before the emulator starts.
    """

    def __init__(self, rom: Rom):
        """Store the ROM copy that will receive instaplay patches.

        Parameters
        ----------
        rom : Rom
            ROM data source used for game data lookups.
        """
        self.rom = rom

    def set_default_powerup(self, powerup: PowerupEntry, with_starman=False):
        # RAM values need to be set via code during run time
        """Patch startup code to grant a default power-up.

        Normal power-ups are written into the title-screen world-map setup.
        P-Wing and Starman require additional runtime RAM writes, so this method
        injects a short routine near the title debug-menu code and disables the
        instruction that would otherwise overwrite the P-Wing display value.

        Parameters
        ----------
        powerup : PowerupEntry
            Power-up entry selected in Foundry settings.
        with_starman : bool, optional
            Whether to also start the level with Star Man state.
        """
        ram_map_power_starman = 0x03F2
        ram_map_power_disp = 0x03F3

        # set default powerup when starting a world
        self.rom.write(Constants.Title_PrepForWorldMap + 0x1, bytes([powerup.power_up_code]))

        if not (powerup.has_p_wing or with_starman):
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

            # there's no known label close to the point in the ROM we need, so this is the best we were able to do
            map_power_disp_reset_address = Constants.WorldMap_Loop - 0x14C
            # We want to delete the 3 byte long STA Map_Power_Disp instruction, which would reset the selected powerup
            # So replace it with three 1-byte NOP instructions, instead
            self.rom.write(map_power_disp_reset_address, bytes([NOP] * 3))

        # add rts, to jump back out of the debug menu
        debug_bytes.append(RTS)

        # We need to start one byte before Title_DebugMenu to remove the RTS of Title_PrepForWorldMap
        # The assembly code below reads as follows:
        self.rom.write(Constants.Title_DebugMenu - 0x1, debug_bytes)

    def put_current_level_to_level_1_1(self, level: Level) -> bool:
        """Redirect the first level tile to the edited level.

        The method writes the active level's object and enemy bytes to their
        ROM addresses, finds the level-1 tile on the selected world map, points
        that tile at the edited level data, and updates the startup world index so
        the temporary ROM boots into the right world.

        Parameters
        ----------
        level : foundry.game.level.Level.Level
            Level being launched through the emulator.

        Returns
        -------
        bool
            ``True`` after the temporary ROM has been patched.

        Raises
        ------
        CantFindFirstTile
            If the selected world map has no level-1 tile.
        LevelNotAttached
            If the level is not attached to ROM addresses.

        Examples
        --------
        The launch path expects a level object that can serialize itself back
        to ROM and expose the world-map metadata needed for redirection.

        >>> from types import SimpleNamespace
        >>> from unittest.mock import Mock, patch
        >>> level = SimpleNamespace(
        ...     attached_to_rom=True,
        ...     world=1,
        ...     object_set_number=3,
        ...     to_bytes=lambda: (
        ...         (0x1F000, bytearray(b"LEVEL")),
        ...         (0x1F200, bytearray(b"ENEMY")),
        ...     ),
        ... )
        >>> world_map = Mock()
        >>> world_map.gen_positions.return_value = iter([SimpleNamespace(tile=lambda: TILE_LEVEL_1)])
        >>> with patch.object(WorldMap, "from_world_number", return_value=world_map):
        ...     player = InstaPlayer(Rom(bytearray(0x40000)))
        ...     player.put_current_level_to_level_1_1(level)
        True
        >>> world_map.replace_level_at_position.call_args[0][0]
        (126976, 127488, 3)
        """
        if not level.attached_to_rom:
            raise LevelNotAttached

        world = level.world

        if world not in range(1, WORLD_COUNT):
            world = 1

        world_map = WorldMap.from_world_number(self.rom, world)

        # find the position of the "level 1" tile in the world map
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
        """Skip the title screen and player-count selection.

        The patch writes the title-screen state RAM value that normally follows
        player selection, then changes a nearby jump to run that injected setup
        code.
        """

        # we have to edit a subroutine, so grab the closest known label and count backwards to get the absolute address
        title_screen_state_injection_abs = Constants.Title_PrepForWorldMap - 13

        title_screen_state_after_player_selection = 0x04
        ram_title_screen_address = 0xDE

        # patch setting the player selection, instead of needing user interaction
        self.rom.write(title_screen_state_injection_abs, LDY_CONST)
        self.rom.write(title_screen_state_injection_abs + 1, title_screen_state_after_player_selection)
        self.rom.write(title_screen_state_injection_abs + 2, STY_RAM)
        self.rom.write(title_screen_state_injection_abs + 3, ram_title_screen_address)

        prg_24_offset = BASE_OFFSET + 24 * PRG_BANK_SIZE - PAGE_A000_OFFSET

        # it's a jump address we need to change now, so make the address relative by subtracting the PRG offset
        title_screen_state_injection_rel = title_screen_state_injection_abs - prg_24_offset

        # we have to path again, so grab the closest known label and count forwards to get the absolute address
        after_player_init = Constants.Do_Title_Screen + 0x4D

        self.rom.write(after_player_init, JSR)
        self.rom.write_little_endian(after_player_init + 1, title_screen_state_injection_rel)

    def skip_world_info_box(self):
        """Shorten the world intro information box.

        The two timer writes reduce delays before control reaches the patched
        world-map level.
        """
        world_info_popup_duration_address_1 = Constants.WorldIntro_BoxTimer_NoSym + 6
        self.rom.write(world_info_popup_duration_address_1, 0x01)

        world_info_popup_duration_address_2 = Constants.LT0 + 8
        self.rom.write(world_info_popup_duration_address_2, 0x01)


def _set_ram_value(value: int, ram_address) -> bytearray:
    """Build 6502 bytes that store a constant into RAM.

    The helper returns ``LDA #value`` followed by ``STA ram_address`` in the
    byte order expected by the NES CPU.

    Parameters
    ----------
    value : int
        Constant loaded into the accumulator.
    ram_address : int
        CPU RAM address written by the generated ``STA`` instruction.

    Returns
    -------
    bytearray
        Assembly statement that writes the RAM value.
    """
    return_bytes = bytearray()

    return_bytes.extend([LDA_CONST, value])

    addr_hi = ram_address >> 8
    addr_lo = ram_address % 2**8

    return_bytes.extend([STA_OFFSET, addr_lo, addr_hi])

    return return_bytes
