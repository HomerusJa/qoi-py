import numpy as np
import numpy.typing as npt
from typing import Annotated
from dataclasses import dataclass
from enum import IntEnum


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
class RGBImage:
    """RGB image with QOI colorspace and shape (height, width, 3)."""

    width: int
    height: int
    colorspace: QOIColorspace
    data: RGBImageContent


@dataclass
class RGBAImage:
    """RGBA image with QOI colorspace and shape (height, width, 4)."""

    width: int
    height: int
    colorspace: QOIColorspace
    data: RGBAImageContent
