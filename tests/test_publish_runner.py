from pathlib import Path

from openpyxl import Workbook

from core.publish_runner import summarize_publish_readiness


def test_summarize_publish_readiness_detects_missing_main_image(tmp_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["笔记内容", "文件位置", "发货属地", "发布情况"])
    folder = tmp_path / "商品A"
    folder.mkdir()
    (folder / "01.jpg").write_bytes(b"x")
    sheet.append(["内容A", str(folder), "杭州", None])
    excel_path = tmp_path / "upload.xlsx"
    workbook.save(excel_path)

    summary = summarize_publish_readiness(excel_path)

    assert summary.pending_count == 1
    assert summary.missing_main_image_count == 1
