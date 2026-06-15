from __future__ import annotations

from pathlib import Path

from .models import PublishDefaultsInput
from vendor.xianyu_uploader.excel import read_pending_rows
from vendor.xianyu_uploader.models import PublishRuntimeConfig, SpecDefinition
from vendor.xianyu_uploader.runner import build_precheck_summary, run_publish_batch


def summarize_publish_readiness(excel_path: str | Path):
    rows = read_pending_rows(Path(excel_path))
    return build_precheck_summary(rows)


def execute_publish(excel_path: str | Path, publisher, defaults: PublishDefaultsInput):
    def runtime_factory(row):
        return PublishRuntimeConfig(
            start_url=defaults.start_url,
            content=row.content,
            location=row.location,
            specs=(
                SpecDefinition(defaults.primary_spec_name, defaults.primary_price, defaults.stock),
                SpecDefinition(defaults.secondary_spec_name, defaults.secondary_price, defaults.stock),
            ),
        )

    return run_publish_batch(
        excel_path=Path(excel_path),
        publisher=publisher,
        runtime_factory=runtime_factory,
    )
