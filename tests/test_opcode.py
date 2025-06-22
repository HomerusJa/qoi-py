from qoi_py.opcodes import QOIOpcode
import pytest


@pytest.mark.parametrize(
    "byte, expected_opcode",
    [
        (0x00, QOIOpcode.INDEX),
        (0x05, QOIOpcode.INDEX),  # Data should be masked out
        (0x40, QOIOpcode.DIFF),
        (0x7F, QOIOpcode.DIFF),  # Data should be masked out
        (0x80, QOIOpcode.LUMA),
        (0xBF, QOIOpcode.LUMA),  # Data should be masked out
        (0xC0, QOIOpcode.RUN),
        (
            0xFC,
            QOIOpcode.RUN,
        ),  # Data should be masked out, should not be mistaken for RGB/RGBA
        (0xFF, QOIOpcode.RGBA),
        (0xFE, QOIOpcode.RGB),
    ],
)
def test_opcode(byte: int, expected_opcode: QOIOpcode):
    """Test the QOIOpcode.from_byte method."""
    assert QOIOpcode.from_byte(byte) == expected_opcode
