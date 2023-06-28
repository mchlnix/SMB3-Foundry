from typing import NewType, TypeAlias, TypeVar

Offset: TypeAlias = int

RawAddress: TypeAlias = int


NormalizedAddress = NewType("NormalizedAddress", RawAddress)
"""
Roms can be expanded to hold more data than the original SMB3 game. This data is added between PRG_029 and PRG_030.

This makes it necessary to reroute any address, that would've gone to the old PRG_030 and PRG_031 to the new PRG_030
and PRG_031.

Since this cannot happen twice, without exceeding the size of the Rom, we have to keep track of which addresses have
already been normalized.

This is done using these types and a type checker, as well as only having 3 methods in the Rom class dealing with
raw Rom data. _read, _write and _find. Any other method using these must normalize their addresses and not give them
out.
"""


AnyAddress = TypeVar("AnyAddress", RawAddress, NormalizedAddress)
