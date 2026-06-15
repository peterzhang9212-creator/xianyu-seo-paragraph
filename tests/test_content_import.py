from pathlib import Path
import re
from zipfile import ZIP_DEFLATED, ZipFile

from openpyxl import Workbook

from core.content_import import load_content_rows


def _write_content_file(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["导出商品名", "标题+正文+标签", "发货属地"])
    sheet.append(["杭州教师SEO资料", "标题A\n正文A\n#标签", "杭州"])
    workbook.save(path)


def test_load_content_rows_reads_template_columns(tmp_path: Path) -> None:
    content_path = tmp_path / "content.xlsx"
    _write_content_file(content_path)

    rows = load_content_rows(content_path)

    assert rows[0].product_name == "杭州教师SEO资料"
    assert rows[0].content == "标题A\n正文A\n#标签"
    assert rows[0].location == "杭州"


def test_load_content_rows_handles_stale_sheet_dimension_metadata(tmp_path: Path) -> None:
    content_path = tmp_path / "content.xlsx"
    _write_content_file(content_path)

    broken_path = tmp_path / "content_stale_dimension.xlsx"
    with ZipFile(content_path, "r") as source_zip, ZipFile(broken_path, "w", ZIP_DEFLATED) as target_zip:
        for member in source_zip.infolist():
            payload = source_zip.read(member.filename)
            if member.filename == "xl/worksheets/sheet1.xml":
                payload = re.sub(br'<dimension ref="[^"]+"/?>', b'<dimension ref="A1:A1"/>', payload, count=1)
            target_zip.writestr(member, payload)

    rows = load_content_rows(broken_path)

    assert rows[0].product_name == "杭州教师SEO资料"
    assert rows[0].content == "标题A\n正文A\n#标签"
    assert rows[0].location == "杭州"
