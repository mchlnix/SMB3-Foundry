from smb3parse.util import Rect


def test_default_parameters():
    rect = Rect()

    assert rect.x == 0
    assert rect.y == 0
    assert rect.width == 0
    assert rect.height == 0


def test_some_parameters():
    rect = Rect(1, 2)

    assert rect.x == 1
    assert rect.y == 2
    assert rect.width == 0
    assert rect.height == 0


def test_all_parameters():
    rect = Rect(1, 2, 3, 4)

    assert rect.x == 1
    assert rect.y == 2
    assert rect.width == 3
    assert rect.height == 4


def test_kw_arguments():
    rect = Rect(y=2, width=3)

    assert rect.x == 0
    assert rect.y == 2
    assert rect.width == 3
    assert rect.height == 0


def test_equality():
    rect = Rect(1, 2, 3, 4)
    rect2 = Rect(1, 2, 3, 4)

    assert rect == rect2


def test_iter():
    rect = Rect(y=2, width=3)

    assert list(rect) == [0, 2, 3, 0]

    assert rect == Rect(*rect)
