from __future__ import annotations

from pathlib import Path

from PIL import Image

from .models import WatermarkSummary
from vendor.batch_watermark_agent import process_directory, suggest_watermark_settings


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def _find_first_image(root: Path) -> Path:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            return path
    raise ValueError("素材目录中没有可处理图片")


def process_product_images(
    *,
    source_root: str | Path,
    watermark_text: str,
    font_scale: float,
    spacing_scale: float,
    opacity: int,
) -> WatermarkSummary:
    source_root = Path(source_root)
    sample_path = _find_first_image(source_root)

    with Image.open(sample_path) as sample_image:
        suggested = suggest_watermark_settings(sample_image.size)

    result = process_directory(
        root=source_root,
        watermark_text=watermark_text,
        font_size=max(12, int(suggested.font_size * font_scale)),
        spacing_scale=spacing_scale,
        opacity=max(0, min(255, opacity)),
        output_suffix="_水印",
        logger=lambda _: None,
    )

    return WatermarkSummary(
        total_count=result.total_count,
        success_count=result.success_count,
        skip_count=result.skip_count,
        output_root=result.output_root,
        oversized_count=len(result.oversized_files),
    )
