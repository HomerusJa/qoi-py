from .types import RGBImage, RGBAImage, QOIChannelCount
from .opcodes import QOIOpcode, MASK_2BIT_DATA
from .header import QOIHeader
from .pixel import Pixel
import numpy as np
from typing import assert_never, overload, Literal


def _wraparound(value: int, min_value: int = 0, max_value: int = 256) -> int:
    """Wrap around a value to be within min_value (inclusive) and max_value (exclusive)

    Examples:
        >>> _wraparound(257)
        1
        >>> _wraparound(-1)
        255
        >>> _wraparound(128, 100, 200)
        128
        >>> _wraparound(99, 100, 200)
        200
        >>> _wraparound(201, 100, 200)
        101
    """
    return (value - min_value) % (max_value - min_value) + min_value


@overload
def qoi_decode(data: bytes, channels: Literal[QOIChannelCount.RGB]) -> RGBImage: ...


@overload
def qoi_decode(data: bytes, channels: Literal[QOIChannelCount.RGBA]) -> RGBAImage: ...


@overload
def qoi_decode(data: bytes, channels: None = None) -> RGBImage | RGBAImage: ...


def qoi_decode(
    data: bytes, channels: QOIChannelCount | None = None
) -> RGBImage | RGBAImage:
    """
    Decode a QOI image from a BytesIO object.

    Args:
        data: The bytes of the QOI image to decode.
        channels: The number of channels to decode. If None, the function will
            determine the channel count from the image header.

    Returns:
        RGBImage | RGBAImage: The decoded image as an RGB or RGBA image.
    """
    header = QOIHeader.from_bytes(data[:14])
    if channels is None:
        channels = header.channels

    running_index: list[Pixel] = [
        Pixel(0, 0, 0, 0) for _ in range(64)
    ]  # FIXME: Is this correct?
    pixel = Pixel(0, 0, 0, 255)
    run_length: int | None = None

    img_data = np.empty((header.height * header.width, channels.value), dtype=np.uint8)
    img_data_pointer = 0

    in_data_pointer = 14
    while (
        in_data_pointer < len(data) - 8
    ):  # Last 8 bytes are padding (7x 0x00 and 1x 0x01)
        byte1 = data[in_data_pointer]
        match QOIOpcode.from_byte(byte1):
            case QOIOpcode.INDEX:
                index = byte1 & MASK_2BIT_DATA
                pixel = running_index[index].copy()

                in_data_pointer += 1
            case QOIOpcode.DIFF:
                # Differences are -2..1
                rdiff = ((byte1 & 0b00110000) >> 4) - 2
                pixel.r = _wraparound(pixel.r + rdiff)
                gdiff = ((byte1 & 0b00001100) >> 2) - 2
                pixel.g = _wraparound(pixel.g + gdiff)
                bdiff = (byte1 & 0b00000011) - 2
                pixel.b = _wraparound(pixel.b + bdiff)
                # alpha is unchanged

                in_data_pointer += 1
            case QOIOpcode.LUMA:
                byte2 = data[in_data_pointer + 1]
                gdiff = (byte1 & 0b00111111) - 32
                rdiff_gdiff = ((byte2 & 0b11110000) >> 4) - 8
                bdiff_gdiff = (byte2 & 0b00001111) - 8

                pixel.r = _wraparound(pixel.r + rdiff_gdiff + gdiff)
                pixel.g = _wraparound(pixel.g + gdiff)
                pixel.b = _wraparound(pixel.b + bdiff_gdiff + gdiff)

                in_data_pointer += 2
            case QOIOpcode.RUN:
                run_length = (byte1 & MASK_2BIT_DATA) + 1
                in_data_pointer += 1
            case QOIOpcode.RGB:
                pixel.r = data[in_data_pointer + 1]
                pixel.g = data[in_data_pointer + 2]
                pixel.b = data[in_data_pointer + 3]
                # alpha stays unchanged

                in_data_pointer += 4  # Opcode + 3 color bytes
            case QOIOpcode.RGBA:
                if channels != QOIChannelCount.RGBA:
                    raise ValueError(
                        "RGBA opcode encountered, but channels is not set to RGBA."
                    )

                pixel.r = data[in_data_pointer + 1]
                pixel.g = data[in_data_pointer + 2]
                pixel.b = data[in_data_pointer + 3]
                pixel.a = data[in_data_pointer + 4]

                in_data_pointer += 5  # Opcode + 4 color bytes

        running_index[pixel.hash()] = pixel.copy()

        for _ in range(run_length if run_length is not None else 1):
            img_data[img_data_pointer][0] = pixel.r
            img_data[img_data_pointer][1] = pixel.g
            img_data[img_data_pointer][2] = pixel.b

            if channels == QOIChannelCount.RGBA:
                img_data[img_data_pointer][3] = pixel.a
            img_data_pointer += 1
        run_length = None

    if channels == QOIChannelCount.RGB:
        return RGBImage(
            width=header.width,
            height=header.height,
            colorspace=header.colorspace,
            data=img_data.reshape((header.height, header.width, 3)),
        )
    elif channels == QOIChannelCount.RGBA:
        return RGBAImage(
            width=header.width,
            height=header.height,
            colorspace=header.colorspace,
            data=img_data.reshape((header.height, header.width, 4)),
        )
    else:
        assert_never()
