import argparse
import math
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Extract the eight intrinsics of a shared OPENCV camera."
    )
    parser.add_argument(
        "model_dir", type=Path, help="Directory containing cameras.txt or camera.txt"
    )
    model_dir = parser.parse_args().model_dir
    camera_file = model_dir / "cameras.txt"
    if not camera_file.is_file():
        camera_file = model_dir / "camera.txt"
    if not camera_file.is_file():
        sys.exit(f"No cameras.txt or camera.txt found in {model_dir}")

    rows = [
        line.split()
        for line in camera_file.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(rows) != 1:
        sys.exit(f"Expected one shared camera in {camera_file}, found {len(rows)}")

    row = rows[0]
    if len(row) != 12 or row[1] != "OPENCV":
        sys.exit(
            f"Expected CAMERA_ID OPENCV WIDTH HEIGHT fx fy cx cy k1 k2 p1 p2 "
            f"in {camera_file}"
        )

    params = row[4:]
    try:
        values = [float(param) for param in params]
    except ValueError:
        sys.exit(f"Invalid numeric camera parameters in {camera_file}")
    if not all(math.isfinite(value) for value in values):
        sys.exit(f"Non-finite camera parameters in {camera_file}")
    if values[0] <= 0 or values[1] <= 0:
        sys.exit(f"Camera focal lengths must be positive in {camera_file}")

    print(
        f"Read camera parameters from {camera_file}: {','.join(params)}",
        file=sys.stderr,
    )
    print(",".join(params))


if __name__ == "__main__":
    main()
