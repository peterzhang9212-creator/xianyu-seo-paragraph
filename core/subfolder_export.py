from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook


class NoSubfoldersFoundError(Exception):
    """Raised when the root directory does not contain any subfolders."""


def collect_subfolder_names(root_path: str | Path) -> list[str]:
    root_path = Path(root_path)
    if not root_path.exists():
        raise FileNotFoundError(f"路径不存在: {root_path}")
    if not root_path.is_dir():
        raise NotADirectoryError(f"输入路径不是文件夹: {root_path}")

    subfolder_names = sorted(item.name for item in root_path.iterdir() if item.is_dir())
    if not subfolder_names:
        raise NoSubfoldersFoundError(f"该目录下没有找到一级子文件夹: {root_path}")
    return subfolder_names


def build_output_path(root_path: str | Path) -> Path:
    root_path = Path(root_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return root_path / f"subfolders_{timestamp}.xlsx"


def export_subfolder_names_to_excel(subfolder_names: list[str], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "子文件夹列表"
    worksheet["A1"] = "子文件夹名称"

    for row_index, folder_name in enumerate(subfolder_names, start=2):
        worksheet.cell(row=row_index, column=1, value=folder_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return output_path
