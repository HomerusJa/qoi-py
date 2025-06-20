from dataclasses import dataclass

from .types import QOIColorspace, QOIChannelCount


@dataclass(frozen=True)
class QOIHeader:
    """A dataclass representing the header of a QOI image file.

    A header is a 14-byte structure that contains metadata about the image.
    The structure is defined as follows:

    ```cpp
    qoi_header {
        char     magic[4];   // magic bytes "qoif"
        uint32_t width;      // image width in pixels (BE)
        uint32_t height;     // image height in pixels (BE)
        uint8_t  channels;   // 3 = RGB, 4 = RGBA
        uint8_t  colorspace; // 0 = sRGB with linear alpha
                                // 1 = all channels linear
    };
    ```
    """

    width: int
    height: int
    channels: QOIChannelCount
    colorspace: QOIColorspace

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create a QOIHeader from bytes and verify it's contents.

        Example usage:
        ```python
        header_bytes = b"qoif\x00\x00\x00\x64\x00\x00\x00\x64\x04\x01"
        header = QOIHeader.from_bytes(header_bytes)
        ```
        """
        if len(data) < 14 or data[:4] != b"qoif":
            raise ValueError("Invalid QOI header")
        width = int.from_bytes(data[4:8], "big")
        height = int.from_bytes(data[8:12], "big")
        channels = QOIChannelCount(data[12])
        colorspace = QOIColorspace(data[13])
        return cls(
            width=width,
            height=height,
            channels=channels,
            colorspace=colorspace,
        )

    def to_bytes(self) -> bytes:
        """Convert the QOIHeader to bytes."""
        magic = b"qoif"
        width = self.width.to_bytes(4, "big")
        height = self.height.to_bytes(4, "big")
        channels = bytes([self.channels.value])
        colorspace = bytes([self.colorspace.value])
        return magic + width + height + channels + colorspace
