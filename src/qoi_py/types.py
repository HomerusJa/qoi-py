import numpy as np
import numpy.typing as npt

from typing import Annotated
from dataclasses import dataclass
from enum import IntEnum


class QOIColorspace(IntEnum):
    SRGB = 0
    LINEAR_RGB = 1


class QOIChannelCount(IntEnum):
    RGB = 3
    RGBA = 4


type RGBImageContent = Annotated[npt.NDArray[np.uint8], ("height", "width", 3)]
type RGBAImageContent = Annotated[npt.NDArray[np.uint8], ("height", "width", 4)]
type ImageContent = RGBAImageContent | RGBImageContent

@dataclass
class RGBImage:
    width: int
    height: int
    colorspace: QOIColorspace
    data: RGBImageContent

@dataclass
class RGBAImage:
    width: int
    height: int
    colorspace: QOIColorspace
    data: RGBAImageContent
