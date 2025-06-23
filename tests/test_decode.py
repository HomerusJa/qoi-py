from qoi_py import qoi_decode, QOIChannelCount, QOIHeader, QOIColorspace

_END_MARKER = b"\x00" * 7 + b"\x01"


def test_decode_minimal_rgb():
    header = QOIHeader(
        width=1,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE), pixel (r=10, g=20, b=30)
    data = header + bytes([0xFE, 10, 20, 30]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)
    assert img.width == 1
    assert img.height == 1
    assert img.data[0, 0, 0] == 10
    assert img.data[0, 0, 1] == 20
    assert img.data[0, 0, 2] == 30


def test_decode_run():
    header = QOIHeader(
        width=4,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE) (r=10, g=20, b=30); run opcode and three pixel run (0xC2) -> bias of -1
    data = header + bytes([0xFE, 10, 20, 30, 0xC2]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)
    assert img.width == 4
    assert img.height == 1

    for i in range(4):
        assert img.data[0][i][0] == 10
        assert img.data[0][i][1] == 20
        assert img.data[0][i][2] == 30


def test_multiple_rgb_pixels():
    header = QOIHeader(
        width=4,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # Three RGB pixels (10, 20, 30), (40, 50, 60), (15, 26, 34)
    data = (
        header
        + bytes([0xFE, 10, 20, 30, 0xFE, 40, 50, 60, 0xFE, 15, 26, 34])
        + _END_MARKER
    )
    row = qoi_decode(data, QOIChannelCount.RGB).data[0]

    assert row[0][0] == 10
    assert row[0][1] == 20
    assert row[0][2] == 30

    assert row[1][0] == 40
    assert row[1][1] == 50
    assert row[1][2] == 60

    assert row[2][0] == 15
    assert row[2][1] == 26
    assert row[2][2] == 34
