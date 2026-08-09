class ParsedLevelObject:
    object_set_number: int
    object_bytes: bytearray
    pos_in_memory: int
    tiles_in_level: list[tuple[int, int]]


class ParsedEnemy:
    object_set_number: int
    object_bytes: bytearray
    pos_in_memory: int


class ParsedLevel:
    object_set_num: int
    graphics_set_num: int
    object_palette_num: int
    enemy_palette_num: int
    screen_memory: bytearray
    parsed_objects: list[ParsedLevelObject]
    parsed_enemies: list[ParsedEnemy]
    object_data_length: int
    enemy_data_length: int

    def has_jump(self)-> bool: ...
    def has_generic_exit(self)-> bool: ...
    def has_big_q_block(self) -> bool: ...

def load_from_address(
        rom_data: bytes,
        prg_bank_count: int,
        object_set_number: int,
        level_position: int,
        enemy_position: int
) -> ParsedLevel:
    ...
