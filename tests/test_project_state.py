from pathlib import Path

from core.models import DefaultsPayload
from core.project_state import ProjectStateStore
from ui.steps.step_upload_sheet import build_initial_material_root


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


def test_upload_step_prefers_last_watermark_output(tmp_path: Path) -> None:
    store = ProjectStateStore(tmp_path / "defaults.json")
    payload = DefaultsPayload()
    payload.state.last_assembly_output = "D:/assembly"
    payload.state.last_watermark_output = "D:/watermark"
    store.save(payload)

    assert build_initial_material_root(store) == "D:/watermark"
