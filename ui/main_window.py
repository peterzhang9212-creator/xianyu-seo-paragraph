from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk

from core.project_state import ProjectStateStore
from ui.steps.step_assembly import AssemblyStepFrame
from ui.steps.step_publish import PublishStepFrame
from ui.steps.step_subfolder_export import SubfolderExportStepFrame
from ui.steps.step_upload_sheet import UploadSheetStepFrame
from ui.steps.step_watermark import WatermarkStepFrame


@dataclass
class AppHandle:
    root: tk.Tk
    nav_buttons: list[ttk.Button]


def _build_state_summary(store: ProjectStateStore) -> str:
    payload = store.load()
    lines = [
        "当前项目状态",
        f"最近组装输出: {payload.state.last_assembly_output or '-'}",
        f"最近水印输出: {payload.state.last_watermark_output or '-'}",
        f"最近正文文件: {payload.state.last_content_path or '-'}",
        f"最近上传表: {payload.state.last_upload_sheet or '-'}",
        f"最近子文件夹导出: {payload.subfolder_export.output_path or '-'}",
    ]
    return "\n".join(lines)


def build_app() -> AppHandle:
    root = tk.Tk()
    root.title("闲鱼教师SEO项目")
    root.geometry("1160x820")

    project_root = Path(__file__).resolve().parents[1]
    store = ProjectStateStore(project_root / "config" / "defaults.json")

    outer = ttk.Frame(root, padding=12)
    outer.pack(fill="both", expand=True)

    nav_frame = ttk.Frame(outer)
    nav_frame.pack(fill="x")

    content_frame = ttk.Frame(outer)
    content_frame.pack(fill="both", expand=True, pady=(12, 0))
    content_frame.columnconfigure(0, weight=4)
    content_frame.columnconfigure(1, weight=2)
    content_frame.rowconfigure(0, weight=1)

    notebook = ttk.Notebook(content_frame)
    notebook.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    state_var = tk.StringVar(value=_build_state_summary(store))

    def refresh_state() -> None:
        state_var.set(_build_state_summary(store))

    _ = [
        AssemblyStepFrame(notebook, store, refresh_state),
        WatermarkStepFrame(notebook, store, refresh_state),
        UploadSheetStepFrame(notebook, store, refresh_state),
        PublishStepFrame(notebook, store, refresh_state),
        SubfolderExportStepFrame(notebook, store, refresh_state),
    ]

    sidebar = ttk.LabelFrame(content_frame, text="项目状态", padding=12)
    sidebar.grid(row=0, column=1, sticky="nsew")
    ttk.Label(sidebar, textvariable=state_var, justify="left").pack(fill="both", expand=True, anchor="nw")

    labels = ["文件组装", "加水印", "生成上传表", "发布设置", "子文件夹工具"]
    nav_buttons: list[ttk.Button] = []
    for index, label in enumerate(labels):
        button = ttk.Button(nav_frame, text=label, command=lambda i=index: notebook.select(i))
        button.pack(side="left", padx=(0, 8))
        nav_buttons.append(button)

    return AppHandle(root=root, nav_buttons=nav_buttons)


def main() -> int:
    app = build_app()
    app.root.mainloop()
    return 0
