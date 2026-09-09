
from pathlib import Path
from PIL import Image, ImageOps
import argparse

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".tif", ".tiff", ".png"}


def normalize_image(src: Path, dst: Path):
    with Image.open(src) as img:
        exif = img.getexif()
        orientation = exif.get(274, 1)

        # 将 EXIF Orientation 对应的旋转/翻转真正应用到像素
        corrected = ImageOps.exif_transpose(img)

        # 保留其他 EXIF 字段，仅将 Orientation 设置为正常方向
        exif[274] = 1

        dst.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs = {}
        if src.suffix.lower() in {".jpg", ".jpeg"}:
            save_kwargs = {
                "quality": 100,
                "subsampling": 0,
            }

        if exif:
            save_kwargs["exif"] = exif.tobytes()

        # 保留 ICC 色彩配置文件
        if "icc_profile" in img.info:
            save_kwargs["icc_profile"] = img.info["icc_profile"]

        corrected.save(dst, **save_kwargs)

        print(
            f"{src.name}: Orientation={orientation}, "
            f"{img.size} -> {corrected.size}"
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path, help="原始图像文件夹")
    parser.add_argument("output_dir", type=Path, help="输出图像文件夹")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    if input_dir == output_dir:
        raise ValueError("输入和输出文件夹不能相同")

    for src in sorted(input_dir.rglob("*")):
        if not src.is_file() or src.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        relative_path = src.relative_to(input_dir)
        dst = output_dir / relative_path
        normalize_image(src, dst)


if __name__ == "__main__":
    main()