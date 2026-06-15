from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd

from .models import AssemblySummary


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def _normalize_path(path: str | Path) -> Path:
    return Path(str(path).strip().strip('"').strip("'"))


def _read_rows(excel_path: Path) -> list[tuple[str, str]]:
    dataframe = pd.read_excel(excel_path, dtype=str)
    if len(dataframe.columns) < 2:
        raise ValueError("城市表至少需要前两列：序号和城市名")
    rows = dataframe.iloc[:, :2].dropna()
    rows.columns = ["sequence", "city"]
    return [(str(row["sequence"]).strip(), str(row["city"]).strip()) for _, row in rows.iterrows()]


def _iter_images(folder: Path) -> list[Path]:
    return sorted(
        [path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES],
        key=lambda path: path.name.casefold(),
    )


def build_materials(
    *,
    excel_path: str | Path,
    parent_folder: str | Path,
    fixed_suffix: str,
    cover_folder: str | Path,
    detail_folder: str | Path,
) -> AssemblySummary:
    excel_path = _normalize_path(excel_path)
    parent_folder = _normalize_path(parent_folder)
    cover_folder = _normalize_path(cover_folder)
    detail_folder = _normalize_path(detail_folder)

    rows = _read_rows(excel_path)
    parent_folder.mkdir(parents=True, exist_ok=True)

    cover_images = {path.stem: path for path in _iter_images(cover_folder)}
    detail_images = _iter_images(detail_folder)

    created_folders = 0
    skipped_folders = 0
    cover_matches = 0
    cover_missing = 0
    detail_copies = 0

    for sequence, city in rows:
        folder_name = f"{city}{fixed_suffix}"
        target_dir = parent_folder / folder_name
        if target_dir.exists():
            skipped_folders += 1
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            created_folders += 1

        (target_dir / "商品标题.txt").write_text(folder_name, encoding="utf-8")

        cover_image = cover_images.get(sequence)
        if cover_image is None:
            cover_missing += 1
        else:
            shutil.copy2(cover_image, target_dir / "商品主图.jpg")
            cover_matches += 1

        for detail_image in detail_images:
            shutil.copy2(detail_image, target_dir / detail_image.name)
            detail_copies += 1

    return AssemblySummary(
        created_folders=created_folders,
        skipped_folders=skipped_folders,
        cover_matches=cover_matches,
        cover_missing=cover_missing,
        detail_copies=detail_copies,
        output_root=parent_folder,
    )
