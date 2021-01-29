from pytest import mark

from foundry.game.gfx.objects.LevelObj.LevelObject import LevelObject, SCREEN_HEIGHT, SCREEN_WIDTH
from foundry.game.ObjectDefinitions import GeneratorType


class FakeObjectSet:
    def __init__(self, orientation: int, has_four_bytes: bool):
        self.orientation = orientation
        self.is_4byte = has_four_bytes

    def get_definition_of(self, _: int):
        return self


level_build_types = [
    False,  # Horizontal
    True,  # Vertical
]

critical_y_pos = [0, 0x1D]
critical_x_pos = [0, 0xB1]
critical_pos = [(x, y) for x in critical_x_pos for y in critical_y_pos]

critical_domains = [1]
critical_gens = [
    (GeneratorType.SINGLE_BLOCK_OBJECT.value, False, 0),
    (GeneratorType.SINGLE_BLOCK_OBJECT.value, False, 0x0B),
    (GeneratorType.HORIZONTAL, True, 0x1B),
    (GeneratorType.HORIZONTAL, False, 0x1B),
    (GeneratorType.HORIZONTAL_2, True, 0x1B),
    (GeneratorType.HORIZONTAL_2, False, 0x1B),
    (GeneratorType.HORIZ_TO_GROUND, False, 0x1B),
    (GeneratorType.VERTICAL, True, 0x1B),
    (GeneratorType.VERTICAL, False, 0x1B),
    (GeneratorType.DIAG_DOWN_LEFT, False, 0x1B),
    (GeneratorType.DESERT_PIPE_BOX, False, 0x00),
    (GeneratorType.DESERT_PIPE_BOX, False, 0x0B),
    (GeneratorType.DIAG_DOWN_RIGHT, False, 0x1B),
    (GeneratorType.DIAG_WEIRD, False, 0x1B),
    (GeneratorType.CENTERED, False, 0x00),
    (GeneratorType.CENTERED, False, 0x0B),
    (GeneratorType.PYRAMID_TO_GROUND, False, 0x00),
    (GeneratorType.PYRAMID_TO_GROUND, False, 0x0B),
    (GeneratorType.PYRAMID_2, False, 0x00),
    (GeneratorType.PYRAMID_2, False, 0x0B),
    (GeneratorType.TO_THE_SKY, False, 0x00),
    (GeneratorType.TO_THE_SKY, False, 0x0B),
    (GeneratorType.ENDING, False, 0x00),
    (GeneratorType.ENDING, False, 0x0B),
]


def create_bytes(pos, domain, index, is_four_bytes, is_vertical) -> bytearray:
    """Generates a bytearray for a test"""
    if is_vertical:
        # Test if it receives the correct offset
        offset = pos[1] // SCREEN_HEIGHT

        pos_main = pos[0] + offset * SCREEN_WIDTH
        pos_sec = pos[1] % SCREEN_HEIGHT
        pos = (pos_main, pos_sec)

    data = bytearray([(domain << 5) + pos[1], pos[0], index])
    if is_four_bytes:
        data.append(0x12)
    return data


@mark.parametrize("level", level_build_types)
@mark.parametrize("x,y", critical_pos)
@mark.parametrize("domain", critical_domains)
@mark.parametrize("gen,is_four_bytes,index", critical_gens)
def test_load_and_save_equal(gen, is_four_bytes, index, domain, x, y, level):
    data = create_bytes((x, y), domain, index, is_four_bytes, level)
    obj = LevelObject.from_bytes(FakeObjectSet(gen, is_four_bytes), data, level)
    assert data == obj.to_bytes(level)


@mark.parametrize("level", level_build_types)
@mark.parametrize("x,y", critical_pos)
@mark.parametrize("new_x,new_y", critical_pos)
@mark.parametrize("domain", critical_domains)
@mark.parametrize("gen,is_four_bytes,index", critical_gens)
def test_changing_pos(gen, is_four_bytes, index, domain, new_x, new_y, x, y, level):
    data = create_bytes((x, y), domain, index, is_four_bytes, level)
    obj = LevelObject.from_bytes(FakeObjectSet(gen, is_four_bytes), data, level)
    obj.position = (new_x, new_y)
    assert create_bytes((new_x, new_y), domain, index, is_four_bytes, level) == obj.to_bytes(level)


@mark.parametrize("level", level_build_types)
@mark.parametrize("x,y", critical_pos)
@mark.parametrize("domain", critical_domains)
@mark.parametrize("gen,is_four_bytes,index", critical_gens)
def test_changing_index(gen, is_four_bytes, index, domain, x, y, level):
    obj = LevelObject.from_bytes(
        FakeObjectSet(gen, is_four_bytes), create_bytes((x, y), domain, index, is_four_bytes, level), level
    )
    obj.index = (index & 0xF0) + 0x03
    assert create_bytes((x, y), domain, (index & 0xF0) + 0x03, is_four_bytes, level) == obj.to_bytes(level)


@mark.parametrize("gen,is_four_bytes,index", critical_gens)
def test_object_bytes(gen, is_four_bytes, index):
    obj = LevelObject(FakeObjectSet(gen, is_four_bytes), 0, index, ((0, 0), (0, 0)))
    assert obj.bytes == 4 if is_four_bytes else 3
