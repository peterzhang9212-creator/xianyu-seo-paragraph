from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AssemblyDefaults:
    excel_path: str = ""
    parent_folder: str = ""
    fixed_suffix: str = ""
    cover_folder: str = ""
    detail_folder: str = ""


@dataclass
class WatermarkDefaults:
    source_root: str = ""
    watermark_text: str = ""
    font_scale: float = 1.0
    spacing_scale: float = 1.0
    opacity: int = 72


@dataclass
class UploadSheetDefaults:
    content_path: str = ""
    material_root: str = ""
    output_path: str = ""


@dataclass
class SubfolderExportDefaults:
    root_path: str = ""
    output_path: str = ""


@dataclass
class PublishDefaults:
    excel_path: str = ""
    primary_spec_name: str = "教育综合（通用）"
    primary_price: str = "8.9"
    secondary_spec_name: str = "专业知识+教育综合"
    secondary_price: str = "17.9"
    stock: int = 200
    start_url: str = "https://www.goofish.com/"


@dataclass
class RuntimeState:
    last_assembly_output: str = ""
    last_watermark_output: str = ""
    last_upload_sheet: str = ""
    last_content_path: str = ""


@dataclass
class DefaultsPayload:
    assembly: AssemblyDefaults = field(default_factory=AssemblyDefaults)
    watermark: WatermarkDefaults = field(default_factory=WatermarkDefaults)
    upload_sheet: UploadSheetDefaults = field(default_factory=UploadSheetDefaults)
    subfolder_export: SubfolderExportDefaults = field(default_factory=SubfolderExportDefaults)
    publish: PublishDefaults = field(default_factory=PublishDefaults)
    state: RuntimeState = field(default_factory=RuntimeState)


@dataclass(frozen=True)
class AssemblySummary:
    created_folders: int
    skipped_folders: int
    cover_matches: int
    cover_missing: int
    detail_copies: int
    output_root: Path


@dataclass(frozen=True)
class WatermarkSummary:
    total_count: int
    success_count: int
    skip_count: int
    output_root: Path
    oversized_count: int


@dataclass(frozen=True)
class ContentRow:
    product_name: str
    content: str
    location: str


@dataclass(frozen=True)
class UploadSheetResult:
    output_path: Path
    matched_count: int


@dataclass(frozen=True)
class PublishDefaultsInput:
    primary_spec_name: str
    primary_price: str
    secondary_spec_name: str
    secondary_price: str
    stock: int
    start_url: str
