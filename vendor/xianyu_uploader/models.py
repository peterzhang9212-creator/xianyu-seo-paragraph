from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpecDefinition:
    name: str
    price: str
    stock: int


@dataclass(frozen=True)
class PublishRow:
    row_index: int
    content: str
    material_dir: Path
    location: str


@dataclass(frozen=True)
class PublishMaterials:
    folder: Path
    main_image: Path
    detail_images: tuple[Path, ...]


@dataclass(frozen=True)
class PublishRuntimeConfig:
    start_url: str
    content: str
    location: str
    specs: tuple[SpecDefinition, SpecDefinition]


@dataclass(frozen=True)
class PrecheckSummary:
    pending_count: int
    missing_folder_count: int
    missing_main_image_count: int
    missing_detail_image_count: int
    missing_location_count: int


@dataclass(frozen=True)
class BatchSummary:
    success_count: int
    failure_count: int
    skipped_count: int
