from dataclasses import dataclass

from .types import QOIColorspace, QOIChannelCount


@dataclass
class QOIHeader:
    magic: bytes
    width: int
    height: int
    channels: QOIChannelCount
    colorspace: QOIColorspace

    @classmethod
    def from_bytes(cls, data: bytes):
        """Create a QOIHeader from bytes and verify it's contents."""
        if len(data) < 14 or data[:4] != b"qoif":
            raise ValueError("Invalid QOI header")
        width = int.from_bytes(data[4:8], "big")
        height = int.from_bytes(data[8:12], "big")
        channels = QOIChannelCount(data[12])
        colorspace = QOIColorspace(data[13])
        return cls(
            magic=data[:4],
            width=width,
            height=height,
            channels=channels,
            colorspace=colorspace,
        )
