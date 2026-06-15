from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.assembly import build_materials


STEP_DESCRIPTION = "根据城市表 Excel、封面图和详情图批量生成商品素材文件夹。输出目录会作为后续步骤的默认素材来源。"


class AssemblyStepFrame(ttk.Frame):
    def __init__(self, master, store, on_state_changed) -> None:
        super().__init__(master, padding=12)
        self.store = store
        self.on_state_changed = on_state_changed
        self.status_var = tk.StringVar(value="待执行")

        payload = store.load()
        self.excel_path_var = tk.StringVar(value=payload.assembly.excel_path)
        self.parent_folder_var = tk.StringVar(value=payload.assembly.parent_folder)
        self.fixed_suffix_var = tk.StringVar(value=payload.assembly.fixed_suffix)
        self.cover_folder_var = tk.StringVar(value=payload.assembly.cover_folder)
        self.detail_folder_var = tk.StringVar(value=payload.assembly.detail_folder)

        master.add(self, text="文件组装")
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text=STEP_DESCRIPTION, justify="left", wraplength=760).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        row = 1
        row = self._add_file_row(
            row,
            "城市表 Excel",
            self.excel_path_var,
            [("Excel 文件", "*.xlsx")],
            False,
            "包含序号和城市名。序号会用来匹配封面图文件名。",
        )
        row = self._add_text_row(
            row,
            "固定后缀",
            self.fixed_suffix_var,
            "会拼到城市名后面，最终组成每个商品文件夹名。",
        )
        row = self._add_folder_row(
            row,
            "输出父目录",
            self.parent_folder_var,
            "程序会在这里批量创建商品子文件夹。",
        )
        row = self._add_folder_row(
            row,
            "封面图目录",
            self.cover_folder_var,
            "封面图文件名要和城市表里的序号一致，例如 001.jpg。",
        )
        row = self._add_folder_row(
            row,
            "详情图目录",
            self.detail_folder_var,
            "这个目录里的详情图会复制到每个商品子文件夹。",
        )

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

    def _choose_file(self, variable: tk.StringVar, filetypes, save: bool) -> None:
        if save:
            selected = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".xlsx")
        else:
            selected = filedialog.askopenfilename(filetypes=filetypes)
        if selected:
            variable.set(selected)

    def _run(self) -> None:
        try:
            summary = build_materials(
                excel_path=self.excel_path_var.get(),
                parent_folder=self.parent_folder_var.get(),
                fixed_suffix=self.fixed_suffix_var.get(),
                cover_folder=self.cover_folder_var.get(),
                detail_folder=self.detail_folder_var.get(),
            )
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f"失败: {exc}")
            messagebox.showerror("文件组装失败", str(exc))
            return

        payload = self.store.load()
        payload.assembly.excel_path = self.excel_path_var.get()
        payload.assembly.parent_folder = self.parent_folder_var.get()
        payload.assembly.fixed_suffix = self.fixed_suffix_var.get()
        payload.assembly.cover_folder = self.cover_folder_var.get()
        payload.assembly.detail_folder = self.detail_folder_var.get()
        payload.state.last_assembly_output = str(summary.output_root)
        self.store.save(payload)
        self.on_state_changed()
        self.status_var.set(
            f"完成: 新建 {summary.created_folders} 个文件夹, 匹配封面 {summary.cover_matches}, 复制详情图 {summary.detail_copies}"
        )
