from .types import RGBImage, RGBAImage, QOIChannelCount
from .header import QOIHeader
from .pixel import Pixel
import numpy as np
from typing import assert_never, overload, Literal


@overload
def qoi_decode(data: bytes, channels: Literal[QOIChannelCount.RGB]) -> RGBImage: ...


@overload
def qoi_decode(data: bytes, channels: Literal[QOIChannelCount.RGBA]) -> RGBAImage: ...


@overload
def qoi_decode(data: bytes, channels: None) -> RGBImage | RGBAImage: ...


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

    # Temporarily rename these to _ to make the type checker happy
    _: list[Pixel | None] = [None for _ in range(64)]
    __ = Pixel(0, 0, 0, 255)

    img_data = np.empty((header.height * header.width, channels.value), dtype=np.uint8)

    pointer = 14
    while pointer < len(data):
        break
        # TODO

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
