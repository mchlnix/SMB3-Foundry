from File import ROM
from Graphics import LevelObjectFactory

THREE_BYTE_ARRAYS = [[0x00, 0x00, 0x00], [0xFF, 0xFF, 0xFF]]

FOUR_BYTE_ARRAYS = [[0x00, 0x00, 0x00, 0x00], [0xFF, 0xFF, 0xFF, 0xFF]]

X_POSITIONS = [0x00, 0xFF]
Y_POSITIONS = [0x00, 0x1F]

OBJ_TYPES = [0x00, 0xFF]
DOMAINS = [0x00, 0x07]
LENGTHS = [0x00, 0xFF]

OBJ_SET = 1
GFX_SET = 1
PALETTE_GROUP_INDEX = 1

ROM.load_from_file("SMB3.nes")


def test_3byte_parsing():
    factory = LevelObjectFactory(OBJ_SET, GFX_SET, PALETTE_GROUP_INDEX)

    for array, x, y, obj_type, domain in zip(
        THREE_BYTE_ARRAYS, X_POSITIONS, Y_POSITIONS, OBJ_TYPES, DOMAINS
    ):
        obj = factory.make_object(array, 0)

        assert obj.x == x
        assert obj.y == y
        assert obj.obj_index == obj_type
        assert obj.domain == domain

    return True
