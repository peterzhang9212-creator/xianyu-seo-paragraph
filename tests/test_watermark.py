from pathlib import Path

from PIL import Image

import vendor.batch_watermark_agent as watermark_agent
from core.watermark import process_product_images


def _save_image(path: Path, color: str) -> None:
    Image.new("RGB", (120, 120), color=color).save(path)


def test_process_product_images_outputs_separate_root(tmp_path: Path) -> None:
    source_root = tmp_path / "materials"
    product_dir = source_root / "杭州教师SEO资料"
    product_dir.mkdir(parents=True)
    _save_image(product_dir / "商品主图.jpg", "white")
    _save_image(product_dir / "detail1.jpg", "blue")

    summary = process_product_images(
        source_root=source_root,
        watermark_text="示例水印",
        font_scale=1.0,
        spacing_scale=1.0,
        opacity=72,
    )

    output_main = summary.output_root / "杭州教师SEO资料" / "商品主图.jpg"
    output_detail = summary.output_root / "杭州教师SEO资料" / "detail1.jpg"
    assert output_main.exists()
    assert output_detail.exists()
    assert summary.output_root != source_root
    assert summary.output_root.name == "materials_水印"
    assert (source_root / "杭州教师SEO资料" / "商品主图.jpg").exists()


def test_process_product_images_reuses_cached_layer_for_same_size_images(tmp_path: Path, monkeypatch) -> None:
    source_root = tmp_path / "batch"
    product_dir = source_root / "商品A"
    product_dir.mkdir(parents=True)
    _save_image(product_dir / "商品主图.jpg", "white")
    _save_image(product_dir / "detail1.jpg", "blue")
    watermark_agent._get_cached_watermark_layer.cache_clear()

    original_builder = watermark_agent._build_watermark_layer
    call_count = 0

    def counting_builder(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return original_builder(*args, **kwargs)

    monkeypatch.setattr(watermark_agent, "_build_watermark_layer", counting_builder)

    process_product_images(
        source_root=source_root,
        watermark_text="缓存测试水印",
        font_scale=1.0,
        spacing_scale=1.0,
        opacity=72,
    )

    assert call_count == 1
