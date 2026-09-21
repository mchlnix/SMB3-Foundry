class ParsedLevelObject:
    object_set_number: int
    object_bytes: bytearray
    pos_in_memory: int
    tiles_in_level: list[tuple[int, int]]

    @property
    def domain(self)-> int: ...

    @property
    def obj_id(self)-> int: ...

    @property
    def is_fixed(self)-> bool: ...

    @property
    def x(self) -> int: ...

    @property
    def y(self)-> int: ...


class ParsedEnemy:
    object_set_number: int
    object_bytes: bytearray
    pos_in_memory: int

    @property
    def domain(self)-> int: ...

    @property
    def obj_id(self)-> int: ...

    @property
    def is_fixed(self)-> bool: ...

    @property
    def x(self)-> int: ...

    @property
    def y(self)-> int: ...

class ParsedLevel:
    object_set_num: int
    graphics_set_num: int
    object_palette_num: int
    enemy_palette_num: int
    screen_memory: list[int]
    parsed_objects: list[ParsedLevelObject]
    parsed_enemies: list[ParsedEnemy]

    @property
    def object_data_length(self)-> int: ...

    @property
    def enemy_data_length(self) -> int: ...

    def has_jump(self)-> bool: ...
    def has_generic_exit(self)-> bool: ...
    def has_big_q_block(self) -> bool: ...

def load_from_address(
        rom_data: bytes,
        prg_bank_count: int,
        object_set_number: int,
        level_position: int,
        enemy_position: int,
        max_steps: int
) -> ParsedLevel:
    ...
