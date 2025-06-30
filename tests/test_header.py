from qoi_py._header import QOIHeader
import pytest


@pytest.mark.parametrize(
    "header_data",
    [
        b"qoif\x00\x00\x00\x05\x00\x00\x00\x08\x03\x00",  # Minimal RGB header, 5x8 pixels
        b"qoif\x00\x00\x00\x02\x00\x00\x00\x05\x04\x00",  # Minimal RGBA header, 2x5 pixels
        b"qoif\x00\x00\x00\x01\x00\x00\x00\x01\x03\x01",  # RGB with sRGB colorspace
        b"qoif\x00\x00\x00\x01\x00\x00\x00\x01\x04\x01",  # RGBA with sRGB colorspace
    ],
)
def test_header_serialization(header_data: bytes):
    assert QOIHeader.from_bytes(header_data).to_bytes() == header_data


# TODO: Add invalid header tests
