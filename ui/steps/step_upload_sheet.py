from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.upload_sheet import generate_upload_sheet


STEP_DESCRIPTION = "把正文模板和素材目录自动拼成上传 Excel。正文里的商品名必须和素材子文件夹名完全一致。"


def build_initial_material_root(store) -> str:
    payload = store.load()
    return payload.state.last_watermark_output or payload.state.last_assembly_output or payload.upload_sheet.material_root


def _default_output_path(material_root: str) -> str:
    if not material_root:
        return ""
    return str(Path(material_root) / "闲鱼自动上传模板.xlsx")


class UploadSheetStepFrame(ttk.Frame):
    def __init__(self, master, store, on_state_changed) -> None:
        super().__init__(master, padding=12)
        self.store = store
        self.on_state_changed = on_state_changed
        self.status_var = tk.StringVar(value="待执行")

        payload = store.load()
        initial_material_root = build_initial_material_root(store)
        output_value = payload.upload_sheet.output_path or _default_output_path(initial_material_root)

        self.content_path_var = tk.StringVar(value=payload.upload_sheet.content_path)
        self.material_root_var = tk.StringVar(value=initial_material_root)
        self.output_path_var = tk.StringVar(value=output_value)

        master.add(self, text="生成上传表")
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text=STEP_DESCRIPTION, justify="left", wraplength=760).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        row = 1
        row = self._add_file_row(
            row,
            "正文模板文件",
            self.content_path_var,
            [("Excel 文件", "*.xlsx")],
            False,
            "选择每次新写好的正文内容表。可直接参考 templates/content_template.xlsx。",
        )
        row = self._add_folder_row(
            row,
            "素材目录",
            self.material_root_var,
            "通常选上一步的“xxx_水印”目录；如果你跳过水印，也可以直接选原素材目录。",
        )
        row = self._add_file_row(
            row,
            "上传表输出文件",
            self.output_path_var,
            [("Excel 文件", "*.xlsx")],
            True,
            "生成后会直接给发布步骤使用。",
        )
        ttk.Button(self, text="开始执行", command=self._run).grid(row=row, column=0, sticky="w", pady=(12, 0))
        ttk.Label(self, textvariable=self.status_var, justify="left").grid(row=row, column=1, sticky="w", pady=(12, 0))

    def _add_folder_row(self, row: int, label: str, variable: tk.StringVar, hint: str) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(self, text="选择...", command=lambda v=variable: self._choose_dir(v)).grid(row=row, column=2, padx=(8, 0), pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _add_file_row(self, row: int, label: str, variable: tk.StringVar, filetypes, save: bool, hint: str) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(
            self,
            text="选择...",
            command=lambda v=variable, ft=filetypes, s=save: self._choose_file(v, ft, s),
        ).grid(row=row, column=2, padx=(8, 0), pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _choose_dir(self, variable: tk.StringVar) -> None:
        selected = filedialog.askdirectory()
        if selected:
            variable.set(selected)
            if not self.output_path_var.get():
                self.output_path_var.set(_default_output_path(selected))

    def _choose_file(self, variable: tk.StringVar, filetypes, save: bool) -> None:
        if save:
            selected = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".xlsx")
        else:
            selected = filedialog.askopenfilename(filetypes=filetypes)
        if selected:
            variable.set(selected)

    def _run(self) -> None:
        try:
            result = generate_upload_sheet(
                content_path=self.content_path_var.get(),
                material_root=self.material_root_var.get(),
                output_path=self.output_path_var.get(),
            )
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f"失败: {exc}")
            messagebox.showerror("生成上传表失败", str(exc))
            return

        payload = self.store.load()
        payload.upload_sheet.content_path = self.content_path_var.get()
        payload.upload_sheet.material_root = self.material_root_var.get()
        payload.upload_sheet.output_path = self.output_path_var.get()
        payload.state.last_content_path = self.content_path_var.get()
        payload.state.last_upload_sheet = str(result.output_path)
        self.store.save(payload)
        self.on_state_changed()
        self.status_var.set(f"完成: 匹配 {result.matched_count} 条, 输出 {result.output_path}")
