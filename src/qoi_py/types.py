import numpy as np
import numpy.typing as npt
from typing import Annotated
from dataclasses import dataclass
from enum import IntEnum


__all__ = [
    "QOIColorspace",
    "QOIChannelCount",
    "RGBImageContent",
    "RGBAImageContent",
    "ImageContent",
    "RGBImage",
    "RGBAImage",
]


class QOIColorspace(IntEnum):
    """QOI colorspace indicator"""

    SRGB = 0
    LINEAR_RGB = 1


class QOIChannelCount(IntEnum):
    """QOI channel count"""

    RGB = 3
    RGBA = 4


RGBImageContent = Annotated[npt.NDArray[np.uint8], ("height", "width", 3)]
"""(height, width, 3) uint8 NumPy array for RGB image data."""

RGBAImageContent = Annotated[npt.NDArray[np.uint8], ("height", "width", 4)]
"""(height, width, 4) uint8 NumPy array for RGBA image data."""

ImageContent = RGBAImageContent | RGBImageContent
"""RGB or RGBA image data as a NumPy array."""


@dataclass
class Image:
    """Image data with shape (height, width, channels) and QOI colorspace"""

    data: ImageContent
    colorspace: QOIColorspace

    @property
    def width(self) -> int:
        """Width of the image."""
        return self.data.shape[1]

    @property
    def height(self) -> int:
        """Height of the image."""
        return self.data.shape[0]

    @property
    def channels(self) -> QOIChannelCount:
        """Number of channels in the image."""
        return QOIChannelCount(self.data.shape[2])


@dataclass
class RGBImage(Image):
    """RGB image data with shape (height, width, 3) and QOI colorspace"""

    data: RGBImageContent

    def __post_init__(self):
        assert self.data.shape[2] == 3, (
            f"RGBImage must have 3 channels, got {self.data.shape[2]}."
        )

    @property
    def channels(self) -> QOIChannelCount:
        """Number of channels in the image."""
        return QOIChannelCount.RGB


@dataclass
class RGBAImage(Image):
    """RGBA image data with shape (height, width, 4) and QOI colorspace"""

    data: RGBAImageContent

    def __post_init__(self):
        assert self.data.shape[2] == 4, (
            f"RGBAImage must have 4 channels, got {self.data.shape[2]}."
        )

    @property
    def channels(self) -> QOIChannelCount:
        """Number of channels in the image."""
        return QOIChannelCount.RGBA
