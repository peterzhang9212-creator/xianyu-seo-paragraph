from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.watermark import process_product_images


STEP_DESCRIPTION = "给主图和详情图统一加水印，并输出到新的“原目录名_水印”目录，不覆盖原图。"


def build_initial_source_root(store) -> str:
    payload = store.load()
    return payload.state.last_assembly_output or payload.watermark.source_root


class WatermarkStepFrame(ttk.Frame):
    def __init__(self, master, store, on_state_changed) -> None:
        super().__init__(master, padding=12)
        self.store = store
        self.on_state_changed = on_state_changed
        self.status_var = tk.StringVar(value="待执行")

        payload = store.load()
        self.source_root_var = tk.StringVar(value=build_initial_source_root(store))
        self.watermark_text_var = tk.StringVar(value=payload.watermark.watermark_text)
        self.font_scale_var = tk.StringVar(value=str(payload.watermark.font_scale))
        self.spacing_scale_var = tk.StringVar(value=str(payload.watermark.spacing_scale))
        self.opacity_var = tk.StringVar(value=str(payload.watermark.opacity))

        master.add(self, text="加水印")
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text=STEP_DESCRIPTION, justify="left", wraplength=760).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        row = 1
        row = self._add_folder_row(
            row,
            "素材目录",
            self.source_root_var,
            "选择上一步生成的商品素材目录，或你手工准备好的现成素材目录。",
        )
        row = self._add_text_row(
            row,
            "水印文字",
            self.watermark_text_var,
            "建议填写固定品牌词、账号词或项目识别词。",
        )
        row = self._add_text_row(
            row,
            "字号倍率",
            self.font_scale_var,
            "想更快一些可用 0.85 到 0.95；字越小，处理通常会略快。",
        )
        row = self._add_text_row(
            row,
            "间距系数",
            self.spacing_scale_var,
            "想更快一些可用 1.15 到 1.35；间距越大，绘制越少。",
        )
        row = self._add_text_row(
            row,
            "透明度",
            self.opacity_var,
            "0 到 255。常用 60 到 90。",
        )

        ttk.Label(self, text="固定规则: 主图和详情图都会加水印，且输出到独立目录。").grid(
            row=row, column=0, columnspan=3, sticky="w", pady=(6, 0)
        )
        row += 1
        ttk.Button(self, text="开始执行", command=self._run).grid(row=row, column=0, sticky="w", pady=(12, 0))
        ttk.Label(self, textvariable=self.status_var, justify="left").grid(row=row, column=1, sticky="w", pady=(12, 0))

    def _add_text_row(self, row: int, label: str, variable: tk.StringVar, hint: str) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _add_folder_row(self, row: int, label: str, variable: tk.StringVar, hint: str) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(self, text="选择...", command=lambda v=variable: self._choose_dir(v)).grid(row=row, column=2, padx=(8, 0), pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _choose_dir(self, variable: tk.StringVar) -> None:
        selected = filedialog.askdirectory()
        if selected:
            variable.set(selected)

    def _run(self) -> None:
        try:
            summary = process_product_images(
                source_root=self.source_root_var.get(),
                watermark_text=self.watermark_text_var.get(),
                font_scale=float(self.font_scale_var.get() or "1.0"),
                spacing_scale=float(self.spacing_scale_var.get() or "1.0"),
                opacity=int(self.opacity_var.get() or "72"),
            )
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f"失败: {exc}")
            messagebox.showerror("加水印失败", str(exc))
            return

        payload = self.store.load()
        payload.watermark.source_root = self.source_root_var.get()
        payload.watermark.watermark_text = self.watermark_text_var.get()
        payload.watermark.font_scale = float(self.font_scale_var.get() or "1.0")
        payload.watermark.spacing_scale = float(self.spacing_scale_var.get() or "1.0")
        payload.watermark.opacity = int(self.opacity_var.get() or "72")
        payload.state.last_watermark_output = str(summary.output_root)
        self.store.save(payload)
        self.on_state_changed()
        self.status_var.set(
            f"完成: 成功 {summary.success_count}, 跳过 {summary.skip_count}, 输出目录 {summary.output_root}"
        )
