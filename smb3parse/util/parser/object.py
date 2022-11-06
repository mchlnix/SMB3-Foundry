from dataclasses import dataclass, field


@dataclass
class ParsedObject:
    object_set_num: int

    obj_bytes: list[int]
    pos_in_mem: int

    tiles_in_level: list[tuple[int, int]] = field(default_factory=list)

    def __str__(self):
        return f"Obj @ {hex(self.pos_in_mem)}: {list(map(hex, self.obj_bytes))}, {self.tiles_in_level}"

    @property
    def domain(self):
        return self.obj_bytes[0] >> 5

    @property
    def obj_id(self):
        return self.obj_bytes[2]

    @property
    def is_fixed(self):
        return self.obj_id < 0x10

    @property
    def x(self):
        return self.obj_bytes[1]

    @property
    def y(self):
        return self.obj_bytes[0] & 0b1_1111


@dataclass
class ParsedEnemy:
    object_set_num: int

    obj_bytes: list[int]
    pos_in_mem: int

    def __str__(self):
        return f"Enemy @ {hex(self.pos_in_mem)}: {list(map(hex, self.obj_bytes))}"

    @property
    def domain(self):
        return 0

    @property
    def obj_id(self):
        return self.obj_bytes[0]

    @property
    def is_fixed(self):
        return True

    @property
    def x(self):
        return self.obj_bytes[1]

    @property
    def y(self):
        return self.obj_bytes[2]
