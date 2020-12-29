

def get_byte_bits(int b, int reverse = 0, int false_value = 0, int true_value = 1):
    """
    Converts a byte to a row 1 bit per pixel row of image data
    :param b: The byte to be converted
    :param reverse: To start from the left or right respectively
    :param false_value: The value of the bit if False
    :param true_value: The value of the bit if True
    :return: A list representation of a bit
    """
    cdef int i
    if reverse:
        return [
        true_value if b & 0b1000_0000 else false_value,
        true_value if b & 0b0100_0000 else false_value,
        true_value if b & 0b0010_0000 else false_value,
        true_value if b & 0b0001_0000 else false_value,
        true_value if b & 0b0000_1000 else false_value,
        true_value if b & 0b0000_0100 else false_value,
        true_value if b & 0b0000_0010 else false_value,
        true_value if b & 0b0000_0001 else false_value
        ]
    else:
                return [
        true_value if b & 0b0000_0001 else false_value,
        true_value if b & 0b0000_0010 else false_value,
        true_value if b & 0b0000_0100 else false_value,
        true_value if b & 0b0000_1000 else false_value,
        true_value if b & 0b0001_0000 else false_value,
        true_value if b & 0b0010_0000 else false_value,
        true_value if b & 0b0100_0000 else false_value,
        true_value if b & 0b1000_0000 else false_value
        ]