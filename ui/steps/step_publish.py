from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.models import PublishDefaultsInput
from core.publish_runner import execute_publish, summarize_publish_readiness


STEP_DESCRIPTION = "先做预检，再发布。发布前请确认 BitBrowser 已打开、闲鱼已登录、上传 Excel 路径正确。"


def build_initial_publish_excel(store) -> str:
    payload = store.load()
    return payload.state.last_upload_sheet or payload.publish.excel_path


class PublishStepFrame(ttk.Frame):
    def __init__(self, master, store, on_state_changed) -> None:
        super().__init__(master, padding=12)
        self.store = store
        self.on_state_changed = on_state_changed
        self.status_var = tk.StringVar(value="待执行")

        payload = store.load()
        self.excel_path_var = tk.StringVar(value=build_initial_publish_excel(store))
        self.primary_spec_name_var = tk.StringVar(value=payload.publish.primary_spec_name)
        self.primary_price_var = tk.StringVar(value=payload.publish.primary_price)
        self.secondary_spec_name_var = tk.StringVar(value=payload.publish.secondary_spec_name)
        self.secondary_price_var = tk.StringVar(value=payload.publish.secondary_price)
        self.stock_var = tk.StringVar(value=str(payload.publish.stock))
        self.start_url_var = tk.StringVar(value=payload.publish.start_url)

        master.add(self, text="发布设置")
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text=STEP_DESCRIPTION, justify="left", wraplength=760).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        row = 1
        row = self._add_file_row(row, "上传 Excel", self.excel_path_var, "选择上一步生成的上传 Excel。")
        row = self._add_text_row(row, "规格1名称", self.primary_spec_name_var, "默认是低价规格。可按你的闲鱼模板改。")
        row = self._add_text_row(row, "规格1价格", self.primary_price_var, "输入数字或带小数的字符串，例如 8.9。")
        row = self._add_text_row(row, "规格2名称", self.secondary_spec_name_var, "默认是高价规格。可按你的闲鱼模板改。")
        row = self._add_text_row(row, "规格2价格", self.secondary_price_var, "输入数字或带小数的字符串，例如 17.9。")
        row = self._add_text_row(row, "库存", self.stock_var, "通常保持 200 即可；需要时你可以手工改。")
        row = self._add_text_row(row, "起始网址", self.start_url_var, "一般保持默认闲鱼首页地址即可。")

        button_row = ttk.Frame(self)
        button_row.grid(row=row, column=0, columnspan=3, sticky="w", pady=(12, 0))
        ttk.Button(button_row, text="执行预检", command=self._run_precheck).pack(side="left")
        ttk.Button(button_row, text="开始发布", command=self._run_publish).pack(side="left", padx=(8, 0))
        ttk.Label(self, textvariable=self.status_var, justify="left").grid(row=row + 1, column=0, columnspan=3, sticky="w", pady=(12, 0))

    def _add_text_row(self, row: int, label: str, variable: tk.StringVar, hint: str) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _add_file_row(self, row: int, label: str, variable: tk.StringVar, hint: str) -> int:
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=6)
        ttk.Button(self, text="选择...", command=lambda v=variable: self._choose_file(v)).grid(row=row, column=2, padx=(8, 0), pady=6)
        ttk.Label(self, text=hint, justify="left", foreground="#666666", wraplength=760).grid(
            row=row + 1, column=1, columnspan=2, sticky="w", pady=(0, 6)
        )
        return row + 2

    def _choose_file(self, variable: tk.StringVar) -> None:
        selected = filedialog.askopenfilename(filetypes=[("Excel 文件", "*.xlsx")])
        if selected:
            variable.set(selected)

    def _save_defaults(self) -> PublishDefaultsInput:
        payload = self.store.load()
        payload.publish.excel_path = self.excel_path_var.get()
        payload.publish.primary_spec_name = self.primary_spec_name_var.get()
        payload.publish.primary_price = self.primary_price_var.get()
        payload.publish.secondary_spec_name = self.secondary_spec_name_var.get()
        payload.publish.secondary_price = self.secondary_price_var.get()
        payload.publish.stock = int(self.stock_var.get() or "200")
        payload.publish.start_url = self.start_url_var.get()
        payload.state.last_upload_sheet = self.excel_path_var.get()
        self.store.save(payload)
        self.on_state_changed()
        return PublishDefaultsInput(
            primary_spec_name=payload.publish.primary_spec_name,
            primary_price=payload.publish.primary_price,
            secondary_spec_name=payload.publish.secondary_spec_name,
            secondary_price=payload.publish.secondary_price,
            stock=payload.publish.stock,
            start_url=payload.publish.start_url,
        )

    def _run_precheck(self) -> None:
        try:
            self._save_defaults()
            summary = summarize_publish_readiness(self.excel_path_var.get())
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f"预检失败: {exc}")
            messagebox.showerror("预检失败", str(exc))
            return

        self.status_var.set(
            "预检完成: "
            f"待发布 {summary.pending_count}, "
            f"缺目录 {summary.missing_folder_count}, "
            f"缺主图 {summary.missing_main_image_count}, "
            f"缺详情图 {summary.missing_detail_image_count}, "
            f"缺发货地 {summary.missing_location_count}"
        )

    def _run_publish(self) -> None:
        try:
            defaults = self._save_defaults()
            from playwright.sync_api import sync_playwright

            from vendor.xianyu_uploader.bitbrowser import connect_xianyu_page
            from vendor.xianyu_uploader.publisher import XianyuPublisher

            with sync_playwright() as playwright:
                browser, page = connect_xianyu_page(playwright)
                try:
                    publisher = XianyuPublisher(page=page)
                    summary = execute_publish(self.excel_path_var.get(), publisher, defaults)
                finally:
                    browser.close()
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f"发布失败: {exc}")
            messagebox.showerror("发布失败", str(exc))
            return

        self.status_var.set(
            f"发布完成: 成功 {summary.success_count}, 失败 {summary.failure_count}, 跳过 {summary.skipped_count}"
        )
