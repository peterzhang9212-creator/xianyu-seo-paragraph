from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from .content_import import load_content_rows
from .models import UploadSheetResult


SHEET2_HEADER_ROWS = [
    ["笔记内容", "文件位置", "发货属地", "发布情况"],
    ["文章标题", None, None, None],
    ["标题控制在20字以内", "建议用软件批量提取，也可以自己写入文件位置到该栏", None, "不用填，发布完写入表格"],
]


def _list_folder_names(material_root: Path) -> list[str]:
    return sorted(path.name for path in material_root.iterdir() if path.is_dir())


def generate_upload_sheet(
    *,
    content_path: str | Path,
    material_root: str | Path,
    output_path: str | Path,
) -> UploadSheetResult:
    content_rows = load_content_rows(content_path)
    material_root = Path(material_root)
    output_path = Path(output_path)

    folder_names = _list_folder_names(material_root)
    content_names = sorted(row.product_name for row in content_rows)
    if folder_names != content_names:
        raise ValueError("正文商品名与素材文件夹名不一致")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet2"
    for header_row in SHEET2_HEADER_ROWS:
        sheet.append(header_row)

    for row in content_rows:
        sheet.append([row.content, str(material_root / row.product_name), row.location, None])

    workbook.create_sheet("Sheet3")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return UploadSheetResult(output_path=output_path, matched_count=len(content_rows))
