from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.subfolder_export import build_output_path, collect_subfolder_names, export_subfolder_names_to_excel


STEP_DESCRIPTION = "按需导出某个根目录下的一级子文件夹名称，供人工核对或后续单独使用。"


class SubfolderExportStepFrame(ttk.Frame):
    def __init__(self, master, store, on_state_changed) -> None:
        super().__init__(master, padding=12)
        self.store = store
        self.on_state_changed = on_state_changed
        self.status_var = tk.StringVar(value="待执行")

        payload = store.load()
        self.root_path_var = tk.StringVar(value=payload.subfolder_export.root_path)
        self.output_path_var = tk.StringVar(value=payload.subfolder_export.output_path)

        master.add(self, text="子文件夹工具")
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text=STEP_DESCRIPTION, justify="left", wraplength=760).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        row = 1
        row = self._add_folder_row(
            row,
            "根目录",
            self.root_path_var,
            "选择要扫描的根目录，只导出它下面的一级子文件夹名称。",
        )
        row = self._add_file_row(
            row,
            "导出 Excel",
            self.output_path_var,
            "默认会导出到根目录下，也可以手工指定别的位置。",
            True,
        )

        ttk.Button(self, text="开始导出", command=self._run).grid(row=row, column=0, sticky="w", pady=(12, 0))
        ttk.Label(self, textvariable=self.status_var, justify="left").grid(row=row, column=1, sticky="w", pady=(12, 0))

    def _add_folder_row(self, row: int, label: str, variable: tk.StringVar, hint: str) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(self, text="选择...", command=lambda v=variable: self._choose_dir(v)).grid(row=row, column=2, padx=(8, 0), pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _add_file_row(self, row: int, label: str, variable: tk.StringVar, hint: str, save: bool) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(self, text="选择...", command=lambda v=variable, s=save: self._choose_file(v, s)).grid(row=row, column=2, padx=(8, 0), pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _choose_dir(self, variable: tk.StringVar) -> None:
        selected = filedialog.askdirectory()
        if selected:
            variable.set(selected)
            if not self.output_path_var.get():
                self.output_path_var.set(str(build_output_path(selected)))

    def _choose_file(self, variable: tk.StringVar, save: bool) -> None:
        selected = filedialog.asksaveasfilename(filetypes=[("Excel 文件", "*.xlsx")], defaultextension=".xlsx") if save else ""
        if selected:
            variable.set(selected)

    def _run(self) -> None:
        try:
            root_path = Path(self.root_path_var.get())
            output_path = Path(self.output_path_var.get()) if self.output_path_var.get() else build_output_path(root_path)
            names = collect_subfolder_names(root_path)
            saved_path = export_subfolder_names_to_excel(names, output_path)
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f"失败: {exc}")
            messagebox.showerror("导出失败", str(exc))
            return

        payload = self.store.load()
        payload.subfolder_export.root_path = self.root_path_var.get()
        payload.subfolder_export.output_path = str(saved_path)
        self.store.save(payload)
        self.on_state_changed()
        self.output_path_var.set(str(saved_path))
        self.status_var.set(f"完成: 已导出 {len(names)} 个子文件夹到 {saved_path}")
