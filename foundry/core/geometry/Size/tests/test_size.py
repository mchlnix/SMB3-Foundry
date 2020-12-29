

import pytest

from foundry.core.geometry.Size.Size import Size


TEST_FLOATING_SIZES = [Size(1.0001, 7.3333), Size(7.3333, 1.0001), Size(41.7171, 7.4545), Size(7.4545, 41.7171)]
TEST_SIZES = [Size(6.5757, 7.3333), Size(7.3333, 6.5757), Size(41, 7), Size(7, 41)]
TEST_NUMS = [1, 7.3333, 41.5757]


def test_initialization():
    """Tests if we can create a size"""
    Size(0, 0)


@pytest.mark.parametrize("test_size", TEST_FLOATING_SIZES)
def test_width_is_an_int(test_size: Size):
    """Tests if width only returns an int"""
    assert test_size.width == int(test_size._width)
    assert test_size.height == int(test_size._height)


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_add_size_with_size(size_0: Size, size_1: Size):
    """Tests if we can add a size with a size"""
    size = size_0 + size_1
    assert size._width == size_0._width + size_1._width
    assert size._height == size_0._height + size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_add_size_with_int(test_size: Size, test_num: int):
    """Tests if we can add a size with an int"""
    size = test_size + test_num
    assert size._width == test_size._width + test_num
    assert size._height == test_size._height + test_num


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_sub_size_with_size(size_0: Size, size_1: Size):
    """Tests if we can subtract a size from a size"""
    size = size_0 - size_1
    assert size._width == size_0._width - size_1._width
    assert size._height == size_0._height - size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_sub_size_with_int(test_size: Size, test_num: int):
    """Tests if we can subtract an int from a size"""
    size = test_size - test_num
    assert size._width == test_size._width - test_num
    assert size._height == test_size._height - test_num


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_sub_int_with_size(test_size: Size, test_num: int):
    """Tests if we can subtract a size from an int"""
    size = test_num - test_size
    assert size._width == test_num - test_size._width
    assert size._height == test_num - test_size._height


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_multiplication_size_with_size(size_0: Size, size_1: Size):
    """Tests if we can multiply a size by a size"""
    size = size_0 * size_1
    assert size._width == size_0._width * size_1._width
    assert size._height == size_0._height * size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_multiplication_int_with_size(test_size: Size, test_num: int):
    """Tests if we can multiply an int by a size"""
    size = test_num * test_size
    assert size._width == test_num * test_size._width
    assert size._height == test_num * test_size._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_multiplication_size_with_int(test_size: Size, test_num: int):
    """Tests if we can multiply a size by an int"""
    size = test_size * test_num
    assert size._width == test_size._width * test_num
    assert size._height == test_size._height * test_num


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_true_divide_size_with_size(size_0: Size, size_1: Size):
    """Tests if we can divide a size by a size"""
    size = size_0 / size_1
    assert size._width == size_0._width / size_1._width
    assert size._height == size_0._height / size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_true_divide_size_with_int(test_size: Size, test_num: int):
    """Tests if we can divide a size by an int"""
    size = test_size / test_num
    assert size._width == test_size._width / test_num
    assert size._height == test_size._height / test_num


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_true_divide_int_with_size(test_size: Size, test_num: int):
    """Tests if we can divide an int by a size"""
    size = test_num / test_size
    assert size._width == test_num / test_size._width
    assert size._height == test_num / test_size._height


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_floor_divide_size_with_size(size_0: Size, size_1: Size):
    """Tests if we can floor divide a size by a size"""
    size = size_0 // size_1
    assert size._width == size_0._width // size_1._width
    assert size._height == size_0._height // size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_floor_divide_size_with_int(test_size: Size, test_num: int):
    """Tests if we can floor divide a size by an int"""
    size = test_size // test_num
    assert size._width == test_size._width // test_num
    assert size._height == test_size._height // test_num


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_floor_divide_int_with_size(test_size: Size, test_num: int):
    """Tests if we can floor divide an int by a size"""
    size = test_num // test_size
    assert size._width == test_num // test_size._width
    assert size._height == test_num // test_size._height


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_modulo_size_with_size(size_0: Size, size_1: Size):
    """Tests if we can mod a size by a size"""
    size = size_0 % size_1
    assert size._width == size_0._width % size_1._width
    assert size._height == size_0._height % size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_modulo_size_with_int(test_size: Size, test_num: int):
    """Tests if we can mod a size by an int"""
    size = test_size % test_num
    assert size._width == test_size._width % test_num
    assert size._height == test_size._height % test_num


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_modulo_int_with_size(test_size: Size, test_num: int):
    """Tests if we can mod an int by a size"""
    size = test_num % test_size
    assert size._width == test_num % test_size._width
    assert size._height == test_num % test_size._height


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_add_size_size(size_0: Size, size_1: Size):
    """Tests if we can add a size"""
    size = Size(size_0._width, size_0._height)
    size += size_1
    assert size._width == size_0._width + size_1._width
    assert size._height == size_0._height + size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_add_size_int(test_size: Size, test_num: int):
    """Tests if we can add an int to a size"""
    size = Size(test_size._width, test_size._height)
    size += test_num
    assert size._width == test_size._width + test_num
    assert size._height == test_size._height + test_num


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_subtract_size_size(size_0: Size, size_1: Size):
    """Tests if we can subtract a size"""
    size = Size(size_0._width, size_0._height)
    size -= size_1
    assert size._width == size_0._width - size_1._width
    assert size._height == size_0._height - size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_subtract_size_int(test_size: Size, test_num: int):
    """Tests if we can subtract an int from a size"""
    size = Size(test_size._width, test_size._height)
    size -= test_num
    assert size._width == test_size._width - test_num
    assert size._height == test_size._height - test_num


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_multiply_size_size(size_0: Size, size_1: Size):
    """Tests if we can multiply a size"""
    size = Size(size_0._width, size_0._height)
    size *= size_1
    assert size._width == size_0._width * size_1._width
    assert size._height == size_0._height * size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_multiply_size_int(test_size: Size, test_num: int):
    """Tests if we can multiply an int from a size"""
    size = Size(test_size._width, test_size._height)
    size *= test_num
    assert size._width == test_size._width * test_num
    assert size._height == test_size._height * test_num


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_true_divide_size_size(size_0: Size, size_1: Size):
    """Tests if we can divide a size"""
    size = Size(size_0._width, size_0._height)
    size /= size_1
    assert size._width == size_0._width / size_1._width
    assert size._height == size_0._height / size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_true_divide_size_int(test_size: Size, test_num: int):
    """Tests if we can divide an int from a size"""
    size = Size(test_size._width, test_size._height)
    size /= test_num
    assert size._width == test_size._width / test_num
    assert size._height == test_size._height / test_num


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_floor_divide_size_size(size_0: Size, size_1: Size):
    """Tests if we can divide a size"""
    size = Size(size_0._width, size_0._height)
    size //= size_1
    assert size._width == size_0._width // size_1._width
    assert size._height == size_0._height // size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_floor_divide_size_int(test_size: Size, test_num: int):
    """Tests if we can divide an int from a size"""
    size = Size(test_size._width, test_size._height)
    size //= test_num
    assert size._width == test_size._width // test_num
    assert size._height == test_size._height // test_num


@pytest.mark.parametrize('size_0', TEST_SIZES)
@pytest.mark.parametrize('size_1', TEST_SIZES)
def test_modulo_size_size(size_0: Size, size_1: Size):
    """Tests if we can mod a size"""
    size = Size(size_0._width, size_0._height)
    size %= size_1
    assert size._width == size_0._width % size_1._width
    assert size._height == size_0._height % size_1._height


@pytest.mark.parametrize('test_size', TEST_SIZES)
@pytest.mark.parametrize('test_num', TEST_NUMS)
def test_modulo_size_int(test_size: Size, test_num: int):
    """Tests if we can mod an int from a size"""
    size = Size(test_size._width, test_size._height)
    size %= test_num
    assert size._width == test_size._width % test_num
    assert size._height == test_size._height % test_num