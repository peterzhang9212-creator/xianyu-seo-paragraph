from ui.main_window import build_app
from ui.steps.step_assembly import STEP_DESCRIPTION as ASSEMBLY_DESCRIPTION
from ui.steps.step_subfolder_export import STEP_DESCRIPTION as EXPORT_DESCRIPTION
from ui.steps.step_watermark import STEP_DESCRIPTION as WATERMARK_DESCRIPTION


def test_build_app_creates_five_step_tabs() -> None:
    app = build_app()
    try:
        labels = [app.nav_buttons[index]["text"] for index in range(5)]
        assert labels == ["文件组装", "加水印", "生成上传表", "发布设置", "子文件夹工具"]
    finally:
        app.root.destroy()


def test_step_descriptions_expose_guidance_text() -> None:
    assert "Excel" in ASSEMBLY_DESCRIPTION
    assert "不覆盖原图" in WATERMARK_DESCRIPTION
    assert "一级子文件夹" in EXPORT_DESCRIPTION
