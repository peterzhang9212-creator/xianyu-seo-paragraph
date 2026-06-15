from pathlib import Path

import pandas as pd
from PIL import Image

from core.assembly import build_materials


def _write_image(path: Path, color: str = "red") -> None:
    Image.new("RGB", (40, 40), color=color).save(path)


def test_build_materials_creates_expected_folder_layout(tmp_path: Path) -> None:
    excel_path = tmp_path / "cities.xlsx"
    pd.DataFrame({"序号": ["001"], "城市": ["杭州"]}).to_excel(excel_path, index=False)

    cover_dir = tmp_path / "covers"
    cover_dir.mkdir()
    _write_image(cover_dir / "001.jpg")

    detail_dir = tmp_path / "details"
    detail_dir.mkdir()
    _write_image(detail_dir / "detail1.jpg", color="blue")
    _write_image(detail_dir / "detail2.jpg", color="green")

    parent_dir = tmp_path / "output"
    parent_dir.mkdir()

    summary = build_materials(
        excel_path=excel_path,
        parent_folder=parent_dir,
        fixed_suffix="教师SEO资料",
        cover_folder=cover_dir,
        detail_folder=detail_dir,
    )

    product_dir = parent_dir / "杭州教师SEO资料"
    assert product_dir.is_dir()
    assert (product_dir / "商品标题.txt").read_text(encoding="utf-8") == "杭州教师SEO资料"
    assert (product_dir / "商品主图.jpg").exists()
    assert (product_dir / "detail1.jpg").exists()
    assert (product_dir / "detail2.jpg").exists()
    assert summary.created_folders == 1
    assert summary.cover_matches == 1
    assert summary.detail_copies == 2
