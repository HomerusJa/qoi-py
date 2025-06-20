from io import BytesIO
from .types import ImageContent


def qoi_decode(data: BytesIO) -> ImageContent: ...
