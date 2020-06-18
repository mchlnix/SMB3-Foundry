from foundry.game.File import ROM

from PySide2.QtCore import QPointF
from PySide2.QtGui import QBrush, QPainter, QPen, Qt

from foundry.game.gfx.drawable.Block import Block
from foundry.game.gfx.objects.LevelObject import GROUND, SCREEN_HEIGHT, SCREEN_WIDTH
from foundry.game.level.Level import Level


AScroll_Movement = 0x13959
AScroll_MovementRepeat = 0x13A47
AScroll_VelAccel = 0x13B35
AScroll_MovementLoopStart = 0x13B38
AScroll_MovementLoop = 0x13B42
AScroll_MovementLoopTicks = 0x13B70
AScroll_HorizontalInitMove = 0x01ECD


HORIZONTAL_SCROLL_0 = 0
HORIZONTAL_SCROLL_1 = 1
UP_RIGHT_DIAG_SCROLL = 2
SPIKE_CEILING_SCROLL = 3
UP_TIL_DOOR_SCROLL = 4
WATER_LEVEL_SCROLL = 5


class AutoScrollDrawer:
    def __init__(self, auto_scroll_row: int, level: Level):
        self.auto_scroll_row = auto_scroll_row
        self.level = level

        self.current_pos = QPointF()
        self.horizontal_speed = 0
        self.vertical_speed = 0

        self.rom = ROM()

        self.pixel_length = 1

        self.acceleration_pen = Qt.NoPen
        self.acceleration_brush = Qt.NoBrush
        self.scroll_pen = Qt.NoPen
        self.scroll_brush = Qt.NoBrush

    def draw(self, painter, block_length: int):
        self.pixel_length = block_length / Block.WIDTH

        self.scroll_brush = QBrush(Qt.blue)
        self.scroll_pen = QPen(self.scroll_brush, 2 * self.pixel_length)

        self.acceleration_brush = QBrush(Qt.red)
        self.acceleration_pen = QPen(self.acceleration_brush, 2 * self.pixel_length)

        painter.setPen(self.scroll_pen)
        painter.setBrush(self.scroll_brush)

        auto_scroll_type_index = self.auto_scroll_row >> 4
        auto_scroll_routine_index = self.auto_scroll_row & 0b0001_1111

        if auto_scroll_type_index in [
            SPIKE_CEILING_SCROLL,
            UP_TIL_DOOR_SCROLL,
            WATER_LEVEL_SCROLL,
            UP_RIGHT_DIAG_SCROLL,
        ]:
            # not visualized
            return
        elif auto_scroll_type_index not in [HORIZONTAL_SCROLL_0, HORIZONTAL_SCROLL_1]:
            # illegal value, those appear in the vanilla ROM, though; so error out
            return

        first_movement_command_index = (
            self.rom.int(AScroll_HorizontalInitMove - 1 + auto_scroll_routine_index) + 1
        ) % 256
        last_movement_command_index = (self.rom.int(AScroll_HorizontalInitMove + auto_scroll_routine_index)) % 256

        self.horizontal_speed = 0
        self.vertical_speed = 0

        self.current_pos = self._determine_auto_scroll_start(block_length)

        for movement_command_index in range(first_movement_command_index, last_movement_command_index + 1):

            movement_command = self.rom.int(AScroll_Movement + movement_command_index)
            movement_repeat = self.rom.int(AScroll_MovementRepeat + movement_command_index)

            self._execute_movement_command(painter, movement_command, movement_repeat)

    def _execute_movement_command(self, painter: QPainter, command: int, repeat: int):
        h_updates_per_tick = 4  # got those by reading the auto scroll routine
        v_updates_per_tick = 2

        is_acceleration_command = (command >> 4) == 0

        if is_acceleration_command:
            # set speed
            h_acceleration_index = (command & 0b00001100) >> 2
            v_acceleration_index = command & 0b00000011

            assert h_acceleration_index != 3
            assert v_acceleration_index != 3

            h_acceleration = self.rom.int(AScroll_VelAccel + h_acceleration_index)
            v_acceleration = self.rom.int(AScroll_VelAccel + v_acceleration_index)

            if h_acceleration == 0xFF:
                h_acceleration = -0x01

            if v_acceleration == 0xFF:
                v_acceleration = -0x01

            h_acceleration <<= 4
            v_acceleration <<= 4

            movement_ticks = repeat
            repeat = 1
        else:
            auto_scroll_loop_selector = command >> 4

            if auto_scroll_loop_selector in [0, 1]:
                # normal movement command
                movement_ticks = self.rom.int(AScroll_MovementLoopStart - 1 + auto_scroll_loop_selector)

                h_acceleration = 0
                v_acceleration = 0
            else:
                # loop command
                movement_loop_start_index = self.rom.int(AScroll_MovementLoopStart - 1 + auto_scroll_loop_selector)
                movement_loop_end_index = self.rom.int(AScroll_MovementLoopStart - 1 + auto_scroll_loop_selector + 1)

                number_of_commands = movement_loop_end_index - movement_loop_start_index

                movement_loop_commands = self.rom.read(
                    AScroll_MovementLoop + movement_loop_start_index, number_of_commands
                )
                movement_loop_repeats = self.rom.read(
                    AScroll_MovementLoopTicks + movement_loop_start_index, number_of_commands
                )

                for _ in range(repeat):
                    for sub_command, sub_repeat in zip(movement_loop_commands, movement_loop_repeats):
                        self._execute_movement_command(painter, sub_command, sub_repeat)

                return

        if is_acceleration_command and (h_acceleration or v_acceleration):
            painter.setPen(self.acceleration_pen)
            painter.setBrush(self.acceleration_brush)
        else:
            painter.setPen(self.scroll_pen)
            painter.setBrush(self.scroll_brush)

        # circle at start of new command
        painter.drawEllipse(self.current_pos, 4 * self.pixel_length, 4 * self.pixel_length)

        if is_acceleration_command and (h_acceleration or v_acceleration):
            for _ in range(movement_ticks):
                self.horizontal_speed += h_acceleration
                self.vertical_speed += v_acceleration

                old_pos = self.current_pos

                self.current_pos += (
                    QPointF(
                        h_updates_per_tick * self.horizontal_speed / 256, v_updates_per_tick * self.vertical_speed / 256
                    )
                    * self.pixel_length
                )

                painter.drawLine(old_pos, self.current_pos)
        else:
            old_pos = QPointF(self.current_pos)

            h_movement = h_updates_per_tick * self.horizontal_speed / 256 * movement_ticks * repeat
            v_movement = v_updates_per_tick * self.vertical_speed / 256 * movement_ticks * repeat

            self.current_pos += QPointF(h_movement, v_movement) * self.pixel_length

            painter.drawLine(old_pos, self.current_pos)

    def _determine_auto_scroll_start(self, block_length: int) -> QPointF:
        # only support horizontal levels for now
        _, mario_y = self.level.header.mario_position()

        scroll_x, scroll_y = SCREEN_WIDTH, min(mario_y + 3, GROUND - SCREEN_HEIGHT // 2)  # height of

        return QPointF(scroll_x, scroll_y) * block_length
