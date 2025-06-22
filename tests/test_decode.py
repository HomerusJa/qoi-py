from qoi_py import qoi_decode, QOIChannelCount, QOIHeader, QOIColorspace


def test_decode_minimal_rgb():
    header = QOIHeader(
        width=1,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE), pixel (r=10, g=20, b=30), end marker
    data = header + bytes([0xFE, 10, 20, 30]) + b"\x00" * 7 + b"\x01"
    img = qoi_decode(data, QOIChannelCount.RGB)
    assert img.width == 1
    assert img.height == 1
    assert img.data[0, 0, 0] == 10
    assert img.data[0, 0, 1] == 20
    assert img.data[0, 0, 2] == 30
