from enum import IntEnum
from typing import Self


MASK_2BIT_OPCODE = 0xC0  # 11000000
MASK_2BIT_DATA = 0x3F  # 00111111


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

        > The 8-bit tags have precedence over the 2-bit tags. A decoder must
          check for the presence of an 8-bit tag first.
          (QOI Specification)

        The function handles this logic.
        """
        if not (0 <= byte < 256):
            raise ValueError("Byte must be in the range 0-255.")

        # First try 8-bit opcodes as defined by the QOI specification
        if byte in (cls.RGB, cls.RGBA):
            return cls(byte)

        # Now, mask to get the first two bits for 2-bit opcodes
        return cls(byte & MASK_2BIT_OPCODE)
