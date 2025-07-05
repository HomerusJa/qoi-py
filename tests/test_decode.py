from qoi_py import qoi_decode
from qoi_py.types import QOIChannelCount, QOIColorspace
from qoi_py._header import QOIHeader

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

    assert (img.height, img.width, img.channels) == (1, 1, QOIChannelCount.RGB)

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

    assert (img.height, img.width, img.channels) == (1, 4, QOIChannelCount.RGB)

    for i in range(4):
        assert img.data[0][i][0] == 10
        assert img.data[0][i][1] == 20
        assert img.data[0][i][2] == 30


def test_decode_rgba_run():
    header = QOIHeader(
        width=4,
        height=1,
        channels=QOIChannelCount.RGBA,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGBA opcode (0xFF) (r=10, g=20, b=30, a=40); run opcode and three pixel run (0xC2) -> bias of -1
    data = header + bytes([0xFF, 10, 20, 30, 40, 0xC2]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGBA)

    assert (img.height, img.width, img.channels) == (1, 4, QOIChannelCount.RGBA)

    for i in range(4):
        assert img.data[0][i][0] == 10
        assert img.data[0][i][1] == 20
        assert img.data[0][i][2] == 30
        assert img.data[0][i][3] == 40


def test_decode_multiple_rgb_pixels():
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
    img = qoi_decode(data, QOIChannelCount.RGB)

    assert (img.height, img.width, img.channels) == (1, 4, QOIChannelCount.RGB)

    row = img.data[0]
    assert row[0][0] == 10
    assert row[0][1] == 20
    assert row[0][2] == 30

    assert row[1][0] == 40
    assert row[1][1] == 50
    assert row[1][2] == 60

    assert row[2][0] == 15
    assert row[2][1] == 26
    assert row[2][2] == 34


def test_decode_multiple_rgba_pixels():
    header = QOIHeader(
        width=3,
        height=1,
        channels=QOIChannelCount.RGBA,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # Three RGBA pixels (10, 20, 30, 255), (40, 50, 60, 230), (15, 26, 34, 120)
    # RGBA marker is 0xFF
    data = (
        header
        + bytes([0xFF, 10, 20, 30, 255, 0xFF, 40, 50, 60, 230, 0xFF, 15, 26, 34, 120])
        + _END_MARKER
    )
    img = qoi_decode(data, QOIChannelCount.RGBA)

    assert (img.height, img.width, img.channels) == (1, 3, QOIChannelCount.RGBA)

    row = img.data[0]
    assert row[0][0] == 10
    assert row[0][1] == 20
    assert row[0][2] == 30
    assert row[0][3] == 255

    assert row[1][0] == 40
    assert row[1][1] == 50
    assert row[1][2] == 60
    assert row[1][3] == 230

    assert row[2][0] == 15
    assert row[2][1] == 26
    assert row[2][2] == 34
    assert row[2][3] == 120


def test_decode_index_rgba():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGBA,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGBA opcode (0xFF) (r=10, g=20, b=30, a=40) -> hash is 12
    # Index opcode (0x00) -> uses the pixel at index 12
    data = header + bytes([0xFF, 10, 20, 30, 40, 0x0C]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGBA)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGBA)

    assert img.data[0][0][0] == 10
    assert img.data[0][0][1] == 20
    assert img.data[0][0][2] == 30
    assert img.data[0][0][3] == 40

    assert img.data[0][1][0] == 10
    assert img.data[0][1][1] == 20
    assert img.data[0][1][2] == 30
    assert img.data[0][1][3] == 40


def test_decode_index_rgb():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE) (r=10, g=20, b=30, (a=255)), alpha implicit -> hash is 9
    # Index opcode (0x00) -> uses the pixel at index 9
    data = header + bytes([0xFE, 10, 20, 30, 0x09]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGB)

    assert img.data[0][0][0] == 10
    assert img.data[0][0][1] == 20
    assert img.data[0][0][2] == 30

    assert img.data[0][1][0] == 10
    assert img.data[0][1][1] == 20
    assert img.data[0][1][2] == 30


def test_decode_diff_rgb():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE) (r=10, g=20, b=30)
    # Diffs can be between -2 and 1 inclusive, saved with a bias of -2
    # Diff opcode (0x80) with rdiff = 1, gdiff = -2, bdiff = 0
    data = header + bytes([0xFE, 10, 20, 30, 0b01110010]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGB)

    assert img.data[0][0][0] == 10
    assert img.data[0][0][1] == 20
    assert img.data[0][0][2] == 30

    assert img.data[0][1][0] == 11  # 10 + 1
    assert img.data[0][1][1] == 18  # 20 - 2
    assert img.data[0][1][2] == 30  # 30 + 0


def test_decode_diff_rgba():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGBA,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGBA opcode (0xFF) (r=10, g=20, b=30, a=40)
    # Diffs can be between -2 and 1 inclusive, saved with a bias of -2
    # Diff opcode (0x80) with rdiff = 1, gdiff = -2, bdiff = 0, alpha must stay unchanged
    # Note: The alpha channel is not affected by the diff opcode.
    data = header + bytes([0xFF, 10, 20, 30, 40, 0b01110010]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGBA)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGBA)

    assert img.data[0][0][0] == 10
    assert img.data[0][0][1] == 20
    assert img.data[0][0][2] == 30
    assert img.data[0][0][3] == 40

    assert img.data[0][1][0] == 11  # 10 + 1
    assert img.data[0][1][1] == 18  # 20 - 2
    assert img.data[0][1][2] == 30  # 30 + 0
    assert img.data[0][1][3] == 40  # alpha stays unchanged


def test_decode_luma_rgb_gdiff_only():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE) (r=40, g=50, b=60)
    # Luma opcode (0x80) with gdiff = -32 (bias of 32), rdiff_gdiff = 0, bdiff_gdiff = 0 (each with a bias of 8)
    data = header + bytes([0xFE, 40, 50, 60, 0b10000000, 0x88]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGB)

    assert img.data[0][0][0] == 40
    assert img.data[0][0][1] == 50
    assert img.data[0][0][2] == 60

    assert img.data[0][1][0] == 8  # r = 40 - 32
    assert img.data[0][1][1] == 18  # g = 50 - 32
    assert img.data[0][1][2] == 28  # b = 60 - 32


def test_decode_luma_rgb_gdiff_only_wraparound_low():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE) (r=10, g=20, b=32)
    # Luma opcode (0x80) with gdiff = -32 (bias of 32), rdiff_gdiff = 0, bdiff_gdiff = 0 (each with a bias of 8)
    data = header + bytes([0xFE, 10, 20, 32, 0b10000000, 0x88]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGB)

    assert img.data[0][0][0] == 10
    assert img.data[0][0][1] == 20
    assert img.data[0][0][2] == 32

    assert img.data[0][1][0] == 234  # r = 10 - 32 + 256 (wraps around)
    assert img.data[0][1][1] == 244  # g = 20 - 32 + 256 (wraps around)
    assert img.data[0][1][2] == 0  # b = 32 - 32


def test_decode_luma_rgb_gdiff_only_wraparound_high():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE) (r=224, g=240, b=250)
    # Luma opcode (0x80) with gdiff = 31 (bias of 32), rdiff_gdiff = 0, bdiff_gdiff = 0 (each with a bias of 8)
    data = header + bytes([0xFE, 224, 240, 250, 0b10111111, 0x88]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGB)

    assert img.data[0][0][0] == 224
    assert img.data[0][0][1] == 240
    assert img.data[0][0][2] == 250

    assert img.data[0][1][0] == 255  # r = 224 + 31
    assert img.data[0][1][1] == 15  # g = 240 + 31 - 256 (wraps around)
    assert img.data[0][1][2] == 25  # b = 250 + 31 - 256 (wraps around)


def test_decode_luma_rgb_all_diffs():
    header = QOIHeader(
        width=2,
        height=1,
        channels=QOIChannelCount.RGB,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # RGB opcode (0xFE) (r=80, g=90, b=100)
    # Luma opcode (0x80) with gdiff = -32 (bias of 32), rdiff_gdiff = -8, bdiff_gdiff = 7 (both with a bias of 8)
    data = header + bytes([0xFE, 80, 90, 100, 0b10000000, 0b00001111]) + _END_MARKER
    img = qoi_decode(data, QOIChannelCount.RGB)

    assert (img.height, img.width, img.channels) == (1, 2, QOIChannelCount.RGB)

    assert img.data[0][0][0] == 80
    assert img.data[0][0][1] == 90
    assert img.data[0][0][2] == 100

    assert img.data[0][1][0] == 40  # r = 80 - 32 - 8
    assert img.data[0][1][1] == 58  # g = 90 - 32
    assert img.data[0][1][2] == 75  # b = 100 - 32 + 7


def test_decode_index_use_multiple_times():
    # Replication of a bug where the index array was using mutable references
    header = QOIHeader(
        width=5,
        height=1,
        channels=QOIChannelCount.RGBA,
        colorspace=QOIColorspace.SRGB,
    ).to_bytes()
    # fmt: off
    data = header + bytes(
        [
            0xFF, 10, 20, 30, 255,  # First pixel (r=10, g=20, b=30, a=255), hash is 9
            0b00001001,             # INDEX opcode (0b00) and index 9
            0xFF, 40, 50, 60, 255,  # Second pixel (r=40, g=50, b=60, a=255), hash is 11
            0b00001011,             # INDEX opcode (0b00) and index 11
            0b00001001,             # INDEX opcode (0b00) and index 9 again  -> This decoded the second pixel before
        ]
    ) + _END_MARKER
    # fmt: on
    img = qoi_decode(data, QOIChannelCount.RGBA)

    assert (img.height, img.width, img.channels) == (1, 5, QOIChannelCount.RGBA)

    px1 = (10, 20, 30, 255)
    px2 = (40, 50, 60, 255)

    assert tuple(img.data[0][0]) == px1
    assert tuple(img.data[0][1]) == px1
    assert tuple(img.data[0][2]) == px2
    assert tuple(img.data[0][3]) == px2
    assert tuple(img.data[0][4]) == px1
