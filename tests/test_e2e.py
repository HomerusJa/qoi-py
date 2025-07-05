from pathlib import Path
import pytest
from PIL import Image
import numpy as np

from typing import Any

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


def mark_stems_as_xfail(
    test_cases: list[tuple[Path, Path]],
    stems: list[str],
    reasons: str | dict[str, str],
) -> list[Any]:
    """Mark specific test cases as expected to fail.

    Args:
        test_cases: The test cases as returned by `get_test_images_map_and_ids`.
        stems: The stems of the test cases to mark as expected to fail.
        reasons: The reason for the expected failure. Can be a single string,
            or a dict mapping stems to reasons.

    Returns:
        A new list of either pytest parameters or the original test cases,
        with the specified stems marked as expected to fail.
    """
    new_test_cases: list[Any] = test_cases.copy()
    for i, (qoi_image, png_image) in enumerate(test_cases):
        if qoi_image.stem in stems:
            if isinstance(reasons, dict):
                reason = reasons.get(qoi_image.stem, "No reason provided")
            else:
                reason = reasons
            new_test_cases[i] = pytest.param(
                qoi_image, png_image, marks=pytest.mark.xfail(reason=reason)
            )
    return new_test_cases


@pytest.mark.e2e
@pytest.mark.parametrize(
    "qoi_image, png_image",
    mark_stems_as_xfail(
        test_cases,
        ["edgecase"],
        (
            "While the QOI image satisfies the QOI spec and specifies it's "
            "channel count as 4, the png image as decoded by PIL has 3 "
            "channels. This leads to a test failure here which needs to be "
            "investigated more deeply."
        ),
    ),
    ids=test_ids,
)
def test_qoi_decode(qoi_image: Path, png_image: Path):
    """Test decoding QOI images to PNG format."""
    qoi_data = qoi_image.read_bytes()

    with Image.open(png_image) as png_pil:
        png_array = np.array(png_pil, dtype=np.uint8)

    res = qoi_decode(qoi_data)

    assert res.data.shape == png_array.shape, "The shapes of the images does not match"
    assert np.array_equal(res.data, png_array), "Decoded data does not match PNG data"


@pytest.mark.e2e
@pytest.mark.parametrize(
    "qoi_image, png_image",
    mark_stems_as_xfail(
        test_cases,
        ["edgecase", "testcard", "testcard_rgba"],
        (
            "These currently do not pass due to issues with the encoder. This "
            "behavior is currently not understood and needs to be investigated."
        ),
    ),
    ids=test_ids,
)
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


@pytest.mark.e2e
@pytest.mark.parametrize(
    "qoi_image, _",
    mark_stems_as_xfail(
        test_cases,
        ["edgecase", "testcard", "testcard_rgba"],
        (
            "These currently do not pass due to issues with the encoder. This "
            "behavior is currently not understood and needs to be investigated."
        ),
    ),
    ids=test_ids,
)
def test_qoi_decode_encode_matches(qoi_image: Path, _):
    """Test that decoding and then encoding a QOI image results in the same data."""
    qoi_data = qoi_image.read_bytes()

    res = qoi_decode(qoi_data)
    res_bytes = qoi_encode(res.data)

    assert len(qoi_data) == len(res_bytes), (
        "The lengths of the original and encoded data do not match"
    )
    assert qoi_data == res_bytes, (
        "The decoded and re-encoded data does not match the original QOI data"
    )
