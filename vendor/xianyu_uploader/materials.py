from __future__ import annotations

from pathlib import Path

from .models import PublishMaterials


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def collect_publish_materials(folder: Path) -> PublishMaterials:
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"素材目录不存在: {folder}")

    files = sorted(
        [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES],
        key=lambda path: path.name.casefold(),
    )
    if not files:
        raise ValueError(f"素材目录内没有图片: {folder}")

    main_image = _find_main_image(files)
    detail_images = tuple(path for path in files if path != main_image)
    return PublishMaterials(folder=folder, main_image=main_image, detail_images=detail_images)


def _find_main_image(files: list[Path]) -> Path:
    for path in files:
        if path.name.casefold() == "商品主图.jpg":
            return path
    raise ValueError("缺少商品主图.jpg")
