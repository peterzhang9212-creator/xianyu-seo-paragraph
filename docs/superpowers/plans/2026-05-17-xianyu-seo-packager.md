# Xianyu SEO Packager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained 4-step desktop app under `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目` that assembles materials, applies watermarks, generates the upload sheet, and launches the existing Xianyu publish flow without depending on the old scattered script directories.

**Architecture:** Keep the business logic in focused `core/` modules with tests first, vendor the existing Xianyu uploader package into the project, then add a thin `tkinter` GUI that drives each step independently and persists last-used values in `config/defaults.json`. Treat step outputs as explicit state so later steps can auto-fill safely but never require strict step-by-step execution.

**Tech Stack:** Python 3.12, tkinter, pathlib, shutil, json, openpyxl, pandas, Pillow, pytest, playwright

---

## File Structure

### New files

- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\app.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\requirements.txt`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\config\defaults.json`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\__init__.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\models.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\project_state.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\assembly.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\watermark.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\content_import.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\upload_sheet.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\publish_runner.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\__init__.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\batch_watermark_agent.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\__init__.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\main_window.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\__init__.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_assembly.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_watermark.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_upload_sheet.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_publish.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\templates\content_template.xlsx`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\docs\使用说明.md`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\docs\维护说明.md`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\conftest.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_project_state.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_assembly.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_watermark.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_content_import.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_upload_sheet.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_publish_runner.py`
- `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_ui_smoke.py`

### Vendored package

- Copy `D:\2 搞钱项目\程序测试\Codex\闲鱼测试\闲鱼自动上传程序\src\xianyu_uploader\*.py`
  to `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\`

### Notes

- The target folder is not currently a git repository, so this plan omits commit steps and uses verification steps instead.
- Tests should set `PYTHONPATH` to the target project root.

### Task 1: Scaffold The Standalone Project

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\app.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\requirements.txt`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\config\defaults.json`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\__init__.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\__init__.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\__init__.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\conftest.py`

- [ ] **Step 1: Write the failing smoke test for imports and state directories**

```python
from pathlib import Path


def test_project_scaffold_paths_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "config").is_dir()
    assert (root / "core").is_dir()
    assert (root / "ui" / "steps").is_dir()
    assert (root / "tests").is_dir()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_project_state.py::test_project_scaffold_paths_exist -v`
Expected: FAIL with `file or directory not found` or missing path assertion errors.

- [ ] **Step 3: Create the minimal scaffold**

```python
# app.py
from ui.main_window import main


if __name__ == "__main__":
    raise SystemExit(main())
```

```text
# requirements.txt
openpyxl>=3.1.0
pandas>=2.2.0
Pillow>=11.0.0
playwright>=1.58.0
pytest>=9.0.0
```

```json
{
  "assembly": {},
  "watermark": {},
  "upload_sheet": {},
  "publish": {},
  "state": {}
}
```

```python
# tests/conftest.py
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_project_state.py::test_project_scaffold_paths_exist -v`
Expected: PASS

### Task 2: Add Persistent Project State

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\models.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\project_state.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_project_state.py`

- [ ] **Step 1: Write failing tests for defaults loading and last-result updates**

```python
from pathlib import Path

from core.project_state import ProjectStateStore


def test_project_scaffold_paths_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / "config").is_dir()
    assert (root / "core").is_dir()
    assert (root / "ui" / "steps").is_dir()
    assert (root / "tests").is_dir()


def test_state_store_returns_default_payload_for_missing_file(tmp_path: Path) -> None:
    store = ProjectStateStore(tmp_path / "defaults.json")
    payload = store.load()
    assert payload.assembly.parent_folder == ""
    assert payload.state.last_assembly_output == ""
    assert payload.publish.stock == 200


def test_state_store_persists_last_outputs(tmp_path: Path) -> None:
    store = ProjectStateStore(tmp_path / "defaults.json")
    payload = store.load()
    payload.assembly.fixed_suffix = "教师SEO资料"
    payload.state.last_assembly_output = "D:/workspace/materials"
    payload.state.last_watermark_output = "D:/workspace/watermarked"
    store.save(payload)

    reloaded = store.load()
    assert reloaded.assembly.fixed_suffix == "教师SEO资料"
    assert reloaded.state.last_assembly_output == "D:/workspace/materials"
    assert reloaded.state.last_watermark_output == "D:/workspace/watermarked"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_project_state.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.project_state'`

- [ ] **Step 3: Write the minimal state models and store**

```python
# core/models.py
from __future__ import annotations

from dataclasses import dataclass, field


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
    publish: PublishDefaults = field(default_factory=PublishDefaults)
    state: RuntimeState = field(default_factory=RuntimeState)
```

```python
# core/project_state.py
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import DefaultsPayload


class ProjectStateStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> DefaultsPayload:
        if not self.path.exists():
            return DefaultsPayload()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        payload = DefaultsPayload()
        for section_name, section_value in data.items():
            if hasattr(payload, section_name):
                target = getattr(payload, section_name)
                for key, value in section_value.items():
                    if hasattr(target, key):
                        setattr(target, key, value)
        return payload

    def save(self, payload: DefaultsPayload) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(payload), ensure_ascii=False, indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_project_state.py -v`
Expected: PASS

### Task 3: Implement Material Assembly Core

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\assembly.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_assembly.py`

- [ ] **Step 1: Write failing tests for folder creation, title files, cover matching, and detail copy**

```python
from pathlib import Path

import pandas as pd
from PIL import Image

from core.assembly import build_materials


def _write_image(path: Path, color: str = "red") -> None:
    Image.new("RGB", (40, 40), color=color).save(path)


def test_build_materials_creates_expected_folder_layout(tmp_path: Path) -> None:
    excel_path = tmp_path / "cities.xlsx"
    pd.DataFrame({"序号": ["001"], "城市": ["杭州"]}).to_excel(excel_path, index=False)

    cover_dir = tmp_path / "covers"
    cover_dir.mkdir()
    _write_image(cover_dir / "001.jpg")

    detail_dir = tmp_path / "details"
    detail_dir.mkdir()
    _write_image(detail_dir / "detail1.jpg", color="blue")
    _write_image(detail_dir / "detail2.jpg", color="green")

    parent_dir = tmp_path / "output"
    parent_dir.mkdir()

    summary = build_materials(
        excel_path=excel_path,
        parent_folder=parent_dir,
        fixed_suffix="教师SEO资料",
        cover_folder=cover_dir,
        detail_folder=detail_dir,
    )

    product_dir = parent_dir / "杭州教师SEO资料"
    assert product_dir.is_dir()
    assert (product_dir / "商品标题.txt").read_text(encoding="utf-8") == "杭州教师SEO资料"
    assert (product_dir / "商品主图.jpg").exists()
    assert (product_dir / "detail1.jpg").exists()
    assert (product_dir / "detail2.jpg").exists()
    assert summary.created_folders == 1
    assert summary.cover_matches == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_assembly.py::test_build_materials_creates_expected_folder_layout -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.assembly'`

- [ ] **Step 3: Write the minimal assembly implementation**

```python
# core/assembly.py
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class AssemblySummary:
    created_folders: int
    cover_matches: int
    detail_copies: int
    output_root: Path


def _read_rows(excel_path: Path) -> list[tuple[str, str]]:
    data = pd.read_excel(excel_path)
    subset = data.iloc[:, :2].dropna()
    subset.columns = ["sequence", "city"]
    return [(str(row["sequence"]).strip(), str(row["city"]).strip()) for _, row in subset.iterrows()]


def build_materials(
    *,
    excel_path: Path,
    parent_folder: Path,
    fixed_suffix: str,
    cover_folder: Path,
    detail_folder: Path,
) -> AssemblySummary:
    rows = _read_rows(Path(excel_path))
    parent_folder = Path(parent_folder)
    cover_images = {path.stem: path for path in Path(cover_folder).iterdir() if path.is_file()}
    detail_images = [path for path in Path(detail_folder).iterdir() if path.is_file()]

    created_folders = 0
    cover_matches = 0
    detail_copies = 0

    for sequence, city in rows:
        folder_name = f"{city}{fixed_suffix}"
        product_dir = parent_folder / folder_name
        if not product_dir.exists():
            product_dir.mkdir(parents=True, exist_ok=True)
            created_folders += 1

        (product_dir / "商品标题.txt").write_text(folder_name, encoding="utf-8")

        if sequence in cover_images:
            shutil.copy2(cover_images[sequence], product_dir / "商品主图.jpg")
            cover_matches += 1

        for detail_image in detail_images:
            shutil.copy2(detail_image, product_dir / detail_image.name)
            detail_copies += 1

    return AssemblySummary(
        created_folders=created_folders,
        cover_matches=cover_matches,
        detail_copies=detail_copies,
        output_root=parent_folder,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_assembly.py::test_build_materials_creates_expected_folder_layout -v`
Expected: PASS

### Task 4: Vendor The Watermark Engine And Implement Independent Output

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\watermark.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\__init__.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\batch_watermark_agent.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_watermark.py`

- [ ] **Step 1: Write failing tests for directory-preserving watermark output**

```python
from pathlib import Path

from PIL import Image

from core.watermark import process_product_images


def _save_image(path: Path, color: str) -> None:
    Image.new("RGB", (120, 120), color=color).save(path)


def test_process_product_images_outputs_separate_root(tmp_path: Path) -> None:
    source_root = tmp_path / "materials"
    product_dir = source_root / "杭州教师SEO资料"
    product_dir.mkdir(parents=True)
    _save_image(product_dir / "商品主图.jpg", "white")
    _save_image(product_dir / "detail1.jpg", "blue")

    summary = process_product_images(
        source_root=source_root,
        watermark_text="示例水印",
        font_scale=1.0,
        spacing_scale=1.0,
        opacity=72,
    )

    output_main = summary.output_root / "杭州教师SEO资料" / "商品主图.jpg"
    output_detail = summary.output_root / "杭州教师SEO资料" / "detail1.jpg"
    assert output_main.exists()
    assert output_detail.exists()
    assert summary.output_root != source_root
    assert (source_root / "杭州教师SEO资料" / "商品主图.jpg").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_watermark.py::test_process_product_images_outputs_separate_root -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.watermark'`

- [ ] **Step 3: Write the minimal watermark wrapper**

```python
# core/watermark.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from vendor.batch_watermark_agent import process_directory, suggest_watermark_settings


@dataclass(frozen=True)
class WatermarkSummary:
    total_count: int
    success_count: int
    skip_count: int
    output_root: Path


def process_product_images(
    *,
    source_root: Path,
    watermark_text: str,
    font_scale: float,
    spacing_scale: float,
    opacity: int,
) -> WatermarkSummary:
    first_image = next(path for path in Path(source_root).rglob("*") if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
    with Image.open(first_image) as image:
        defaults = suggest_watermark_settings(image.size)
    result = process_directory(
        root=source_root,
        watermark_text=watermark_text,
        font_size=max(12, int(defaults.font_size * font_scale)),
        spacing_scale=spacing_scale,
        opacity=opacity,
        logger=lambda _: None,
    )
    return WatermarkSummary(
        total_count=result.total_count,
        success_count=result.success_count,
        skip_count=result.skip_count,
        output_root=result.output_root,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_watermark.py::test_process_product_images_outputs_separate_root -v`
Expected: PASS

- [ ] **Step 5: Copy the watermark engine into the project**

Run: `Copy-Item 'D:\2 搞钱项目\程序测试\Codex\水印测试\batch_watermark_agent.py' 'D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\batch_watermark_agent.py'`
Expected: the vendored watermark module exists under `vendor\batch_watermark_agent.py`

### Task 5: Implement Content Import And Upload Sheet Generation

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\content_import.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\upload_sheet.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_content_import.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_upload_sheet.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\templates\content_template.xlsx`

- [ ] **Step 1: Write failing tests for content validation and upload sheet output**

```python
from pathlib import Path

from openpyxl import Workbook, load_workbook

from core.content_import import load_content_rows
from core.upload_sheet import generate_upload_sheet


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


def test_generate_upload_sheet_matches_folder_names(tmp_path: Path) -> None:
    content_path = tmp_path / "content.xlsx"
    _write_content_file(content_path)
    material_root = tmp_path / "materials"
    (material_root / "杭州教师SEO资料").mkdir(parents=True)
    output_path = tmp_path / "upload.xlsx"

    result = generate_upload_sheet(
        content_path=content_path,
        material_root=material_root,
        output_path=output_path,
    )

    saved = load_workbook(result.output_path)
    try:
        sheet = saved.active
        assert sheet.cell(row=4, column=1).value == "标题A\n正文A\n#标签"
        assert sheet.cell(row=4, column=2).value == str(material_root / "杭州教师SEO资料")
        assert sheet.cell(row=4, column=3).value == "杭州"
    finally:
        saved.close()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_content_import.py tests/test_upload_sheet.py -v`
Expected: FAIL with missing module errors.

- [ ] **Step 3: Write the minimal content and upload-sheet implementation**

```python
# core/content_import.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl import load_workbook


@dataclass(frozen=True)
class ContentRow:
    product_name: str
    content: str
    location: str


def load_content_rows(path: Path) -> list[ContentRow]:
    workbook = load_workbook(path, read_only=True)
    try:
        sheet = workbook.active
        headers = [str(cell.value).strip() if cell.value else "" for cell in next(sheet.iter_rows(max_row=1))]
        required = ["导出商品名", "标题+正文+标签", "发货属地"]
        index_map = {name: headers.index(name) for name in required}
        rows: list[ContentRow] = []
        for values in sheet.iter_rows(min_row=2, values_only=True):
            if not any(values):
                continue
            rows.append(
                ContentRow(
                    product_name=str(values[index_map["导出商品名"]]).strip(),
                    content=str(values[index_map["标题+正文+标签"]]).strip(),
                    location=str(values[index_map["发货属地"]]).strip(),
                )
            )
        return rows
    finally:
        workbook.close()
```

```python
# core/upload_sheet.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook

from .content_import import load_content_rows


SHEET2_HEADER_ROWS = [
    ["笔记内容", "文件位置", "发货属地", "发布情况"],
    ["文章标题", None, None, None],
    ["标题控制在20字以内", "建议用软件批量提取，也可以自己写入文件位置到该栏", None, "不用填，发布完写入表格"],
]


@dataclass(frozen=True)
class UploadSheetResult:
    output_path: Path
    matched_count: int


def generate_upload_sheet(*, content_path: Path, material_root: Path, output_path: Path) -> UploadSheetResult:
    rows = load_content_rows(content_path)
    folder_names = sorted(path.name for path in Path(material_root).iterdir() if path.is_dir())
    content_names = [row.product_name for row in rows]
    if folder_names != sorted(content_names):
        raise ValueError("正文商品名与素材文件夹名不一致")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet2"
    for header_row in SHEET2_HEADER_ROWS:
        sheet.append(header_row)
    for row in rows:
        sheet.append([row.content, str(Path(material_root) / row.product_name), row.location, None])
    workbook.create_sheet("Sheet3")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)
    return UploadSheetResult(output_path=output_path, matched_count=len(rows))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_content_import.py tests/test_upload_sheet.py -v`
Expected: PASS

- [ ] **Step 5: Create the bundled content template**

```python
from openpyxl import Workbook

workbook = Workbook()
sheet = workbook.active
sheet.title = "正文模板"
sheet.append(["导出商品名", "标题+正文+标签", "发货属地"])
sheet.append(["杭州教师SEO资料", "标题示例\n正文示例\n#标签1 #标签2", "杭州"])
workbook.save(r"D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\templates\content_template.xlsx")
```

Run: `python -c "<script above>"`
Expected: template file created at `templates/content_template.xlsx`

### Task 6: Vendor The Existing Xianyu Uploader And Add Publish Runner

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\__init__.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\bitbrowser.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\cli.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\config.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\excel.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\logging_utils.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\materials.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\models.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\publisher.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\vendor\xianyu_uploader\runner.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\core\publish_runner.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_publish_runner.py`

- [ ] **Step 1: Write failing tests for a publish precheck wrapper**

```python
from pathlib import Path

from openpyxl import Workbook

from core.publish_runner import summarize_publish_readiness


def test_summarize_publish_readiness_detects_missing_main_image(tmp_path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["笔记内容", "文件位置", "发货属地", "发布情况"])
    folder = tmp_path / "商品A"
    folder.mkdir()
    sheet.append(["内容A", str(folder), "杭州", None])
    excel_path = tmp_path / "upload.xlsx"
    workbook.save(excel_path)

    summary = summarize_publish_readiness(excel_path)

    assert summary.pending_count == 1
    assert summary.missing_main_image_count == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_publish_runner.py::test_summarize_publish_readiness_detects_missing_main_image -v`
Expected: FAIL with missing module errors.

- [ ] **Step 3: Copy the uploader package and write the wrapper**

```python
# core/publish_runner.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vendor.xianyu_uploader.excel import read_pending_rows
from vendor.xianyu_uploader.runner import build_precheck_summary, run_publish_batch
from vendor.xianyu_uploader.models import SpecDefinition, PublishRuntimeConfig


@dataclass(frozen=True)
class PublishDefaultsInput:
    primary_spec_name: str
    primary_price: str
    secondary_spec_name: str
    secondary_price: str
    stock: int
    start_url: str


def summarize_publish_readiness(excel_path: Path):
    rows = read_pending_rows(Path(excel_path))
    return build_precheck_summary(rows)


def execute_publish(excel_path: Path, publisher, defaults: PublishDefaultsInput):
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_publish_runner.py::test_summarize_publish_readiness_detects_missing_main_image -v`
Expected: PASS

### Task 7: Build The Tkinter Step UI

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\main_window.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_assembly.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_watermark.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_upload_sheet.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_publish.py`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\tests\test_ui_smoke.py`

- [ ] **Step 1: Write the failing smoke test for window construction**

```python
# tests/test_ui_smoke.py
from ui.main_window import build_app


def test_build_app_creates_four_step_tabs() -> None:
    app = build_app()
    try:
        labels = [app.nav_buttons[index]["text"] for index in range(4)]
        assert labels == ["文件组装", "加水印", "生成上传表", "发布设置"]
    finally:
        app.root.destroy()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_publish_runner.py tests/test_project_state.py tests/test_assembly.py tests/test_watermark.py tests/test_content_import.py tests/test_upload_sheet.py -v`
Expected: FAIL with missing `ui.main_window` import.

- [ ] **Step 3: Write the minimal UI shell and per-step panels**

```python
# ui/main_window.py
from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk

from core.project_state import ProjectStateStore
from ui.steps.step_assembly import AssemblyStepFrame
from ui.steps.step_publish import PublishStepFrame
from ui.steps.step_upload_sheet import UploadSheetStepFrame
from ui.steps.step_watermark import WatermarkStepFrame


@dataclass
class AppHandle:
    root: tk.Tk
    nav_buttons: list[ttk.Button]


def build_app() -> AppHandle:
    root = tk.Tk()
    root.title("闲鱼教师SEO项目")
    store = ProjectStateStore(Path(__file__).resolve().parents[1] / "config" / "defaults.json")

    nav_frame = ttk.Frame(root)
    nav_frame.pack(fill="x", padx=12, pady=12)
    body = ttk.Notebook(root)
    body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    AssemblyStepFrame(body, store)
    WatermarkStepFrame(body, store)
    UploadSheetStepFrame(body, store)
    PublishStepFrame(body, store)

    labels = ["文件组装", "加水印", "生成上传表", "发布设置"]
    buttons: list[ttk.Button] = []
    for index, label in enumerate(labels):
        button = ttk.Button(nav_frame, text=label, command=lambda i=index: body.select(i))
        button.pack(side="left", padx=4)
        buttons.append(button)
    return AppHandle(root=root, nav_buttons=buttons)


def main() -> int:
    app = build_app()
    app.root.mainloop()
    return 0
```

```python
# ui/steps/step_assembly.py
from __future__ import annotations

from tkinter import ttk


class AssemblyStepFrame(ttk.Frame):
    def __init__(self, master, store) -> None:
        super().__init__(master)
        master.add(self, text="文件组装")
        ttk.Label(self, text="文件组装").pack(anchor="w", padx=12, pady=12)
```

```python
# ui/steps/step_watermark.py
from __future__ import annotations

from tkinter import ttk


class WatermarkStepFrame(ttk.Frame):
    def __init__(self, master, store) -> None:
        super().__init__(master)
        master.add(self, text="加水印")
        ttk.Label(self, text="加水印").pack(anchor="w", padx=12, pady=12)
```

```python
# ui/steps/step_upload_sheet.py
from __future__ import annotations

from tkinter import ttk


class UploadSheetStepFrame(ttk.Frame):
    def __init__(self, master, store) -> None:
        super().__init__(master)
        master.add(self, text="生成上传表")
        ttk.Label(self, text="生成上传表").pack(anchor="w", padx=12, pady=12)
```

```python
# ui/steps/step_publish.py
from __future__ import annotations

from tkinter import ttk


class PublishStepFrame(ttk.Frame):
    def __init__(self, master, store) -> None:
        super().__init__(master)
        master.add(self, text="发布设置")
        ttk.Label(self, text="发布设置").pack(anchor="w", padx=12, pady=12)
```

- [ ] **Step 4: Run the smoke test**

Run: `python -m pytest tests/test_ui_smoke.py::test_build_app_creates_four_step_tabs -v`
Expected: PASS

### Task 8: Connect Each Step To Real Actions And Saved Defaults

**Files:**
- Modify: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\main_window.py`
- Modify: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_assembly.py`
- Modify: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_watermark.py`
- Modify: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_upload_sheet.py`
- Modify: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\ui\steps\step_publish.py`

- [ ] **Step 1: Write the failing integration test for saved defaults auto-fill**

```python
from pathlib import Path

from core.models import DefaultsPayload
from core.project_state import ProjectStateStore
from ui.steps.step_upload_sheet import build_initial_material_root


def test_upload_step_prefers_last_watermark_output(tmp_path: Path) -> None:
    store = ProjectStateStore(tmp_path / "defaults.json")
    payload = DefaultsPayload()
    payload.state.last_assembly_output = "D:/assembly"
    payload.state.last_watermark_output = "D:/watermark"
    store.save(payload)

    assert build_initial_material_root(store) == "D:/watermark"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_project_state.py::test_upload_step_prefers_last_watermark_output -v`
Expected: FAIL with missing helper or wrong value.

- [ ] **Step 3: Wire helpers, save callbacks, and auto-detection rules**

```python
# ui/steps/step_upload_sheet.py
from __future__ import annotations

from tkinter import ttk


def build_initial_material_root(store) -> str:
    payload = store.load()
    return payload.state.last_watermark_output or payload.state.last_assembly_output or payload.upload_sheet.material_root


class UploadSheetStepFrame(ttk.Frame):
    def __init__(self, master, store) -> None:
        super().__init__(master)
        master.add(self, text="生成上传表")
        ttk.Label(self, text="生成上传表").pack(anchor="w", padx=12, pady=12)
        ttk.Label(self, text=build_initial_material_root(store)).pack(anchor="w", padx=12, pady=4)
```

- Add the same concrete helpers in the other step files:

```python
# ui/steps/step_watermark.py
def build_initial_source_root(store) -> str:
    payload = store.load()
    return payload.state.last_assembly_output or payload.watermark.source_root
```

```python
# ui/steps/step_publish.py
def build_initial_publish_excel(store) -> str:
    payload = store.load()
    return payload.state.last_upload_sheet or payload.publish.excel_path
```

For each step frame, implement the same three actions explicitly:
- create `tk.StringVar` fields from the helper defaults
- run the corresponding `core.*` function on `开始执行`
- update both the step-specific section and the matching `payload.state.last_*` value through `ProjectStateStore.save()`

- [ ] **Step 4: Run the integration test**

Run: `python -m pytest tests/test_project_state.py::test_upload_step_prefers_last_watermark_output -v`
Expected: PASS

### Task 9: Write User And Maintenance Docs

**Files:**
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\docs\使用说明.md`
- Create: `D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\docs\维护说明.md`

- [ ] **Step 1: Draft the user-facing instructions**

```markdown
# 使用说明

## 启动

1. 安装依赖：`python -m pip install -r requirements.txt`
2. 启动程序：`python app.py`

## 四步流程

1. 文件组装：选择城市表、父目录、固定后缀、封面图目录、详情图目录
2. 加水印：选择素材目录，输入水印文字，系统会输出独立水印目录
3. 生成上传表：选择正文模板文件和素材目录，生成上传 Excel
4. 发布设置：选择上传 Excel，确认规格、价格、库存，连接 BitBrowser 后执行

## 跳步规则

- 可以直接进入任何一步
- 若存在最近一次输出，程序会自动回填
- 若同时存在多个候选目录，程序只提示，不会自动替你选择
```

- [ ] **Step 2: Draft the maintenance instructions**

```markdown
# 维护说明

## 关键模块

- `core/assembly.py`：文件组装逻辑
- `core/watermark.py`：水印输出逻辑
- `core/content_import.py`：正文模板导入
- `core/upload_sheet.py`：上传表生成
- `core/publish_runner.py`：发布流程包装
- `vendor/xianyu_uploader/`：闲鱼自动发布底层逻辑
- `config/defaults.json`：最近输入和默认参数

## 常见修改入口

- 改主图固定文件名：`core/assembly.py` 和 `vendor/xianyu_uploader/materials.py`
- 改正文模板列：`core/content_import.py`
- 改上传表头：`core/upload_sheet.py`
- 改发布默认规格价格：`config/defaults.json` 和 `core/models.py`
```

- [ ] **Step 3: Save the docs and verify they exist**

Run: `Get-ChildItem 'D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\docs'`
Expected: output includes `使用说明.md` and `维护说明.md`

### Task 10: Final Verification

**Files:**
- Verify only

- [ ] **Step 1: Run the full test suite**

Run: `python -m pytest tests -v`
Expected: PASS

- [ ] **Step 2: Run a local smoke launch**

Run: `python app.py`
Expected: the `闲鱼教师SEO项目` window opens with four navigation buttons and step panels.

- [ ] **Step 3: Verify the bundled template exists**

Run: `Get-Item 'D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目\templates\content_template.xlsx'`
Expected: file exists.

- [ ] **Step 4: Verify the app is self-contained**

Run: `Get-ChildItem -Recurse 'D:\2 搞钱项目\程序测试\好用的封装程序\闲鱼教师SEO项目' | Select-String -Pattern 'claude code插件代码|闲鱼自动表格生成|闲鱼自动上传程序|自动获取子文件名'`
Expected: only documentation may mention the old paths; runtime code should not import from the old scattered project directories.
