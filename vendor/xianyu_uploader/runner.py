from __future__ import annotations

from pathlib import Path

from .excel import read_pending_rows, write_publish_status
from .materials import collect_publish_materials
from .models import BatchSummary, PrecheckSummary
from .publisher import PublishNeedsManualReview


def build_precheck_summary(rows) -> PrecheckSummary:
    missing_folder_count = 0
    missing_main_image_count = 0
    missing_detail_image_count = 0
    missing_location_count = 0

    for row in rows:
        if not row.material_dir.exists():
            missing_folder_count += 1
            continue

        try:
            materials = collect_publish_materials(row.material_dir)
        except FileNotFoundError:
            missing_folder_count += 1
            continue
        except ValueError as exc:
            if "商品主图.jpg" in str(exc):
                missing_main_image_count += 1
            continue

        if not materials.detail_images:
            missing_detail_image_count += 1
        if not row.location:
            missing_location_count += 1

    return PrecheckSummary(
        pending_count=len(rows),
        missing_folder_count=missing_folder_count,
        missing_main_image_count=missing_main_image_count,
        missing_detail_image_count=missing_detail_image_count,
        missing_location_count=missing_location_count,
    )


def run_publish_batch(*, excel_path: Path, publisher, runtime_factory) -> BatchSummary:
    rows = read_pending_rows(excel_path)
    success_count = 0
    failure_count = 0
    skipped_count = 0

    for row in rows:
        try:
            materials = collect_publish_materials(row.material_dir)
        except Exception as exc:  # noqa: BLE001
            write_publish_status(excel_path, row.row_index, f"失败：{exc}")
            failure_count += 1
            continue

        for attempt in range(2):
            try:
                runtime = runtime_factory(row)
                publisher.publish(materials=materials, runtime=runtime)
                write_publish_status(excel_path, row.row_index, "成功")
                success_count += 1
                break
            except PublishNeedsManualReview as exc:
                write_publish_status(excel_path, row.row_index, f"待确认：{exc}")
                skipped_count += 1
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 1:
                    write_publish_status(excel_path, row.row_index, f"失败：{exc}")
                    failure_count += 1

    return BatchSummary(
        success_count=success_count,
        failure_count=failure_count,
        skipped_count=skipped_count,
    )
