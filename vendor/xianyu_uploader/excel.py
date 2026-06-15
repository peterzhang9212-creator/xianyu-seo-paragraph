from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from .models import PublishRow


EXPECTED_HEADERS = {
    "content": "笔记内容",
    "material_dir": "文件位置",
    "location": "发货属地",
    "status": "发布情况",
}


def normalize_user_path(raw: str) -> Path:
    cleaned = raw.strip().strip('"').strip("'")
    return Path(cleaned).expanduser()


def read_pending_rows(excel_path: Path) -> list[PublishRow]:
    workbook = load_workbook(excel_path)
    try:
        sheet = workbook.active
        header_map = _read_header_map(sheet)
        rows: list[PublishRow] = []
        for row_index in range(2, sheet.max_row + 1):
            status = sheet.cell(row=row_index, column=header_map["status"]).value
            if status not in (None, ""):
                continue

            content = str(sheet.cell(row=row_index, column=header_map["content"]).value or "").strip()
            material_raw = str(sheet.cell(row=row_index, column=header_map["material_dir"]).value or "").strip()
            location = str(sheet.cell(row=row_index, column=header_map["location"]).value or "").strip()
            if not content or not material_raw:
                continue

            rows.append(
                PublishRow(
                    row_index=row_index,
                    content=content,
                    material_dir=normalize_user_path(material_raw),
                    location=location,
                )
            )
        return rows
    finally:
        workbook.close()


def write_publish_status(excel_path: Path, row_index: int, status_text: str) -> None:
    workbook = load_workbook(excel_path)
    try:
        sheet = workbook.active
        header_map = _read_header_map(sheet)
        sheet.cell(row=row_index, column=header_map["status"]).value = status_text
        workbook.save(excel_path)
    finally:
        workbook.close()


def _read_header_map(sheet) -> dict[str, int]:
    result: dict[str, int] = {}
    for col_index in range(1, sheet.max_column + 1):
        header = str(sheet.cell(row=1, column=col_index).value or "").strip()
        for key, expected in EXPECTED_HEADERS.items():
            if header == expected:
                result[key] = col_index

    missing = [key for key in EXPECTED_HEADERS if key not in result]
    if missing:
        raise ValueError(f"Excel 缺少必要列: {', '.join(EXPECTED_HEADERS[key] for key in missing)}")
    return result
