from enum import IntEnum
from typing import Self


class QOIOpcode(IntEnum):
    """A QOI opcode."""

    INDEX = 0x00  # 00xxxxxx
    DIFF = 0x40  # 01xxxxxx
    LUMA = 0x80  # 10xxxxxx
    RUN = 0xC0  # 11xxxxxx
    RGB = 0xFE  # 11111110
    RGBA = 0xFF  # 11111111

    @classmethod
    def from_byte(cls, byte: int) -> Self:
        """Get the opcode from a byte (0-255).

        As defined by the QOI specification, the 8-bit opcodes are tried first,
        and if the byte does not match any of those, the first two bits are
        masked to get the 2-bit opcodes.
        """
        if not (0 <= byte < 256):
            raise ValueError("Byte must be in the range 0-255.")

        # First try 8-bit opcodes as defined by the QOI specification
        if byte in (cls.RGB, cls.RGBA):
            return cls(byte)

        # Now, mask to get the first two bits for 2-bit opcodes
        return cls(byte & 0xC0)
