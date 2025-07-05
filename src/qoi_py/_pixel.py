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

    def __post_init__(self):
        """Ensure that the pixel values are in the range [0, 255]."""
        for value in (self.r, self.g, self.b, self.a):
            assert isinstance(value, int), (
                f"Pixel value {value} is not an integer. "
                "Ensure that the pixel values are integers in this range. "
                f"{self!r}"
            )

            assert 0 <= value <= 255, (
                f"Pixel value {value} is out of range [0, 255]. "
                "Ensure that the pixel values are integers in this range. "
                f"{self!r}"
            )
