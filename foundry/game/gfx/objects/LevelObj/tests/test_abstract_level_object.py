from pytest import mark

from foundry.game.gfx.objects.LevelObj.AbstractLevelObject import AbstractLevelObject


class FakeObjectSet:
    def __init__(self):
        self.orientation = 0

    def get_definition_of(self, type: int):
        self.orientation = type + 1
        return self


class GenericLevelObject(AbstractLevelObject):
    @property
    def width(self) -> int:
        return super().width

    @width.setter
    def width(self, width: int) -> None:
        self._width = width

    @property
    def height(self) -> int:
        return super().height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def x(self) -> int:
        return super().x

    @x.setter
    def x(self, x: int) -> None:
        self._x = x

    @property
    def y(self) -> int:
        return super().y

    @y.setter
    def y(self, y: int) -> None:
        self._y = y


def test_initialization():
    GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))


def test_orientation():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.orientation == 1


@mark.parametrize(
    "index,domain,expected",
    [(0, 0, 0), (1, 0, 1), (0x10, 0, 0x10), (0x11, 0, 0x10), (0x20, 0, 0x11), (0xFF, 0, 0x1E), (0, 1, 0x1F)],
)
def test_type(index, domain, expected):
    obj = GenericLevelObject(FakeObjectSet(), domain, index, ((0, 0), (0, 0)))
    assert obj.type == expected


def test_getting_width():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.width == 0
    obj._width = 1
    assert obj.width == 1


def test_getting_height():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.height == 0
    obj._height = 1
    assert obj.height == 1


def test_getting_x():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.x == 0
    obj._x = 1
    assert obj.x == 1


def test_getting_y():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.y == 0
    obj._y = 1
    assert obj.y == 1


def test_position():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.position == (0, 0)
    obj.position = (1, 2)
    assert obj.position == (1, 2)


def test_size():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.size == (0, 0)
    obj.size = (1, 2)
    assert obj.size == (1, 2)


def test_rect():
    obj = GenericLevelObject(FakeObjectSet(), 0, 0, ((0, 0), (0, 0)))
    assert obj.rect == ((0, 0), (0, 0))
    obj.rect = ((0, 1), (2, 3))
    assert obj.rect == ((0, 1), (2, 3))
