from PIL import Image
import numpy as np
from qoi_py import qoi_decode
import sys
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / "tests" / "assets"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_decode_comparison.py <image_name>")
        sys.exit(1)

    image_name = sys.argv[1]
    if image_name.endswith(".qoi") or image_name.endswith(".png"):
        image_name = image_name[:-4]

    qoi_path = ASSETS_DIR / f"{image_name}.qoi"
    png_path = ASSETS_DIR / f"{image_name}.png"

    if not qoi_path.exists() or not png_path.exists():
        print(f"Files {qoi_path} or {png_path} do not exist.")
        sys.exit(1)

    with Image.open(png_path) as img:
        print(f"Decoding PNG image: {png_path}")
        original_array = np.array(img)

    with open(qoi_path, "rb") as f:
        print(f"Decoding QOI image: {qoi_path}")
        decoded_array = qoi_decode(f.read()).data

    if original_array.shape != decoded_array.shape:
        print(
            f"Shape mismatch: original {original_array.shape}, decoded {decoded_array.shape}"
        )
        sys.exit(1)

    if np.array_equal(original_array, decoded_array):
        print("The original and decoded images are identical.")
        print(
            f"{original_array.shape[0]} rows, {original_array.shape[1]} columns, {original_array.shape[2]} channels"
        )
        sys.exit(0)

    height, width, channels = original_array.shape
    output_path = Path() / f"compare_{image_name}.txt"

    with output_path.open("w") as f:
        # Write header based on channel count
        if channels == 3:
            f.write(
                f"{'i':>3} {'j':>3} | {'r1':>3} {'g1':>3} {'b1':>3}   | {'r2':>3} {'g2':>3} {'b2':>3} | {'!':>1}\n"
            )
            f.write("-" * 37 + "\n")
        elif channels == 4:
            f.write(
                f"{'i':>3} {'j':>3} | {'r1':>3} {'g1':>3} {'b1':>3} {'a1':>3} | {'r2':>3} {'g2':>3} {'b2':>3} {'a2':>3} | {'!':>1}\n"
            )
            f.write("-" * 45 + "\n")
        else:
            print(f"Unsupported channel count: {channels}")
            sys.exit(1)

        # Write pixel data
        for i in range(height):
            for j in range(width):
                orig_px = original_array[i, j]
                decoded_px = decoded_array[i, j]
                is_mismatch = not np.array_equal(orig_px, decoded_px)
                marker = "*" if is_mismatch else ""

                if channels == 3:
                    r1, g1, b1 = orig_px
                    r2, g2, b2 = decoded_px
                    line = f"{i:3d} {j:3d} | {r1:3d} {g1:3d} {b1:3d}   | {r2:3d} {g2:3d} {b2:3d} | {marker}\n"
                else:  # channels == 4
                    r1, g1, b1, a1 = orig_px
                    r2, g2, b2, a2 = decoded_px
                    line = f"{i:3d} {j:3d} | {r1:3d} {g1:3d} {b1:3d} {a1:3d} | {r2:3d} {g2:3d} {b2:3d} {a2:3d} | {marker}\n"

                f.write(line)

    print(f"Comparison saved to: {output_path}")
