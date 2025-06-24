from pathlib import Path
import pytest
from PIL import Image
import numpy as np

from qoi_py import qoi_decode, qoi_encode


def get_test_images_map_and_ids() -> tuple[list[tuple[Path, Path]], list[str]]:
    assets_path = (Path(__file__).parent / "assets").resolve()
    test_cases = [
        (qoi, qoi.with_suffix(".png"))
        for qoi in assets_path.glob("*.qoi")
        if (qoi.with_suffix(".png")).exists()
    ]
    test_ids = [f"{qoi.stem}" for (qoi, _) in test_cases]
    return test_cases, test_ids


test_cases, test_ids = get_test_images_map_and_ids()


@pytest.mark.xfail(reason="Implementation has bugs")
@pytest.mark.e2e
@pytest.mark.parametrize("qoi_image, png_image", test_cases, ids=test_ids)
def test_qoi_decode(qoi_image: Path, png_image: Path):
    """Test decoding QOI images to PNG format."""
    qoi_data = qoi_image.read_bytes()

    with Image.open(png_image) as png_pil:
        png_array = np.array(png_pil, dtype=np.uint8)

    res = qoi_decode(qoi_data)

    assert (res.width, res.height) == res.data.shape[:2], (
        "The data provided about the image dimensions is not consistent"
    )
    assert res.data.shape == png_array.shape, "The shapes of the images does not match"
    assert np.array_equal(res.data, png_array), "Decoded data does not match PNG data"


@pytest.mark.skip(reason="Not implemented")
@pytest.mark.e2e
@pytest.mark.parametrize("qoi_image, png_image", test_cases, ids=test_ids)
def test_qoi_encode(qoi_image: Path, png_image: Path):
    """Test encoding numpy arrays to QOI format."""
    qoi_data = qoi_image.read_bytes()

    with Image.open(png_image) as png_pil:
        png_array = np.array(png_pil, dtype=np.uint8)

    res_bytes = qoi_encode(png_array)

    assert len(qoi_data) == len(res_bytes), (
        "The lengths of the two results does not match"
    )
    assert qoi_data == res_bytes, (
        "The encoded image does not match the content of the test image"
    )
