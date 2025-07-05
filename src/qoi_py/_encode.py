from .types import ImageContent, QOIColorspace, QOIChannelCount
from ._structure import QOIHeader, END_MARKER
from ._pixel import Pixel
from ._opcodes import QOIOpcode


def _write_run_length(data: bytearray, run_length: int) -> None:
    """
    Write the run length to the data bytearray.

    Args:
        data (bytearray): The bytearray to write to.
        run_length (int): The run length to write.
    """
    assert 1 <= run_length <= 62, "Run length must be between 1 and 62 inclusive."
    data.append(QOIOpcode.RUN | (run_length - 1))


def qoi_encode(
    image: ImageContent, colorspace: QOIColorspace = QOIColorspace.SRGB
) -> bytes:
    """
    Encode an image to QOI format.

    Args:
        image (ImageContent): The image to encode, which can be either RGB or
            RGBA. The array will never be mutated.

    Returns:
        bytes: The encoded QOI image data.
    """
    data = bytearray()

    width, height, channels = (
        image.shape[1],
        image.shape[0],
        QOIChannelCount(image.shape[2]),
    )
    data.extend(
        QOIHeader(
            width=width,
            height=height,
            colorspace=colorspace,
            channels=channels,
        ).to_bytes()
    )

    previous_pixel = Pixel(0, 0, 0, 255)
    run_length = 0

    # 64-entry running pixel index
    running_index: list[Pixel] = [Pixel(0, 0, 0, 0) for _ in range(64)]

    # flatten image into list of pixels
    flat_pixels = image.reshape(-1, image.shape[2])
    print(f"{flat_pixels.shape=}, {flat_pixels.dtype=}")

    for raw_pixel in flat_pixels:
        # create a Pixel object from raw data
        current_pixel = Pixel(
            r=int(raw_pixel[0]),
            g=int(raw_pixel[1]),
            b=int(raw_pixel[2]),
            a=int(raw_pixel[3]) if channels == QOIChannelCount.RGBA else 255,
        )

        # Check for run
        if current_pixel == previous_pixel:
            run_length += 1
            if run_length == 62:
                _write_run_length(data, run_length)
                run_length = 0
            previous_pixel = current_pixel
            continue

        # If there was a run pending, write it out now
        if run_length > 0:
            _write_run_length(data, run_length)
            run_length = 0

        index_pos = current_pixel.hash()

        # Check index match
        if current_pixel == running_index[index_pos]:
            data.append(QOIOpcode.INDEX | index_pos)
            previous_pixel = current_pixel
            continue

        # Update the index with the current pixel
        running_index[index_pos] = current_pixel

        # Check alpha difference
        if previous_pixel.a != current_pixel.a:
            data.extend(
                [
                    QOIOpcode.RGBA,
                    current_pixel.r,
                    current_pixel.g,
                    current_pixel.b,
                    current_pixel.a,
                ]
            )
            previous_pixel = current_pixel
            continue

        # color channel diffs
        rdiff = current_pixel.r - previous_pixel.r
        gdiff = current_pixel.g - previous_pixel.g
        bdiff = current_pixel.b - previous_pixel.b

        # Small diff
        if -2 <= rdiff <= 1 and -2 <= gdiff <= 1 and -2 <= bdiff <= 1:
            data.append(
                QOIOpcode.DIFF | ((rdiff + 2) << 4) | ((gdiff + 2) << 2) | (bdiff + 2)
            )
            previous_pixel = current_pixel
            continue

        # Luma diff
        rdiff_gdiff = rdiff - gdiff
        bdiff_gdiff = bdiff - gdiff

        if -8 <= rdiff_gdiff <= 7 and -8 <= bdiff_gdiff <= 7 and -32 <= gdiff <= 31:
            data.extend(
                [
                    QOIOpcode.LUMA | (gdiff + 32),
                    ((rdiff_gdiff + 8) << 4) | (bdiff_gdiff + 8),
                ]
            )
            previous_pixel = current_pixel
            continue

        # Fallback to RGB opcode
        data.extend([QOIOpcode.RGB, current_pixel.r, current_pixel.g, current_pixel.b])

        previous_pixel = current_pixel

    # There might be a final run left to flush
    if run_length > 0:
        _write_run_length(data, run_length)

    # Append the end marker
    data.extend(END_MARKER)

    return bytes(data)
