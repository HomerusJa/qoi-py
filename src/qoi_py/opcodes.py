from enum import IntEnum
from typing import Self


class QOI2BitOpcode(IntEnum):
    """All two-bit opcodes in QOI format.

    Only the first two bits are significant; the last six bits are used for data.
    """

    INDEX = 0x00  # 00xxxxxx
    DIFF = 0x40  # 01xxxxxx
    LUMA = 0x80  # 10xxxxxx
    RUN = 0xC0  # 11xxxxxx

    @classmethod
    def from_byte(cls, byte: int) -> Self:
        """Get the opcode from a byte (0-255)."""
        if not (0 <= byte < 256):
            raise ValueError("Byte must be in the range 0-255.")
        return cls(byte & 0xC0)  # Mask to get the first two bits


class QOIByteOpcode(IntEnum):
    RGB = 0xFE  # 11111110
    RGBA = 0xFF  # 11111111
