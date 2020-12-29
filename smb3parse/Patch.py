from ips_util import Patch as IPS


def safe_patch(original: str, base: str, new: str, out: str):
    """
    Provides a patch that only edits what it needs compared against an original rom.
    This allows for the patch to only edit what it needs compared to a regular patch that will
    override preexisting patches.
    :param original: The original rom to be compared against
    :param base: The rom to be patched
    :param new: The rom with the changes yet to be added
    :param out: The name of the rom patched
    """
    patch = Patch.from_files(original, new)
    with open(base, 'rb') as base_rom:
        with open(out, 'w+b') as patched_rom:
            patched_rom.write(patch.apply(base_rom.read()))


def get_bytes_from_file(filename):
    return open(filename, "rb").read()


class Patch(IPS):
    @classmethod
    def from_files(cls, original: str, new: str):
        """
        Generates a patch from two file paths
        :param original: The original path to be compared against
        :param new: The new data to be patched
        :return: A patch with the updated patch
        """
        return cls.from_bytes(get_bytes_from_file(original), get_bytes_from_file(new))

    @classmethod
    def from_bytes(cls, original: bytes, new: bytes):
        """
        Generates a patch from two bytes
        :param original: The original byte array to be compared against
        :param new: The new data to be patched
        :return: A patch with the updated patch
        """
        print(hex(len(original)), hex(len(new)))
        patch = Patch()
        in_patch = False
        start = 0
        for idx, byte in enumerate(new):
            if len(original) < idx + 1 or byte != original[idx]:
                if not in_patch:
                    in_patch = True
                    start = idx
                    print(hex(start))
                if in_patch and idx - start > 0xFFF0:
                    in_patch = False
                    patch.add_record(start, new[start: idx])
            elif in_patch:
                in_patch = False
                patch.add_record(start, new[start: idx])
        if in_patch:
            patch.add_record(start, new[start:])
        return patch
