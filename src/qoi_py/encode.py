from io import BytesIO
from .types import ImageContent


def qoi_encode(image: ImageContent) -> BytesIO: ...
