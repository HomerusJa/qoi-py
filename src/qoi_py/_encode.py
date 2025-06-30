from .types import ImageContent, QOIColorspace, QOIChannelCount
from ._header import QOIHeader


def qoi_encode(
    image: ImageContent, colorspace: QOIColorspace = QOIColorspace.SRGB
) -> bytes:
    """
    Encode an image to QOI format.

    Args:
        image (ImageContent): The image to encode, which can be either RGB or RGBA.

    Returns:
        bytes: The encoded QOI image data.
    """
    data = bytearray()
    header = QOIHeader(
        width=image.shape[1],
        height=image.shape[0],
        colorspace=colorspace,
        channels=QOIChannelCount.RGBA if image.shape[2] == 4 else QOIChannelCount.RGB,
    )
    data.extend(header.to_bytes())

    return bytes(data)
