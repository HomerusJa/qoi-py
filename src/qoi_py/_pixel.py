from dataclasses import dataclass


@dataclass(frozen=True)
class Pixel:
    """A dataclass representing a pixel in an image.

    This class is used to represent a pixel in an image, with RGB or RGBA values.
    The values are stored as integers in the range [0, 255].
    """

    r: int
    g: int
    b: int
    a: int

    def hash(self) -> int:
        """Return the hash for the place in the running array."""
        return (self.r * 3 + self.g * 5 + self.b * 7 + self.a * 11) % 64
