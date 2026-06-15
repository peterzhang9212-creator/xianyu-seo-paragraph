from __future__ import annotations

import argparse
import builtins
from pathlib import Path

from playwright.sync_api import sync_playwright

from .bitbrowser import connect_xianyu_page
from .config import StartupDefaults
from .logging_utils import build_run_logger
from .models import PublishRuntimeConfig, SpecDefinition
from .publisher import XianyuPublisher
from .runner import run_publish_batch

input = builtins.input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="使用当前 BitBrowser 自动发布闲鱼商品")
    parser.add_argument("--excel", type=Path, help="要处理的 Excel 文件")
    return parser


def pick_excel_file() -> Path | None:
    try:
        from tkinter import Tk, filedialog
    except Exception:
        return None

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askopenfilename(
            title="请选择要发布商品的 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx")],
        )
    finally:
        root.destroy()
    return Path(selected) if selected else None


def collect_startup_defaults() -> StartupDefaults:
    excel_path = pick_excel_file()
    if excel_path is None:
        raise SystemExit("未选择 Excel，程序已退出")

    primary_spec_name = input("请输入规格1名称，直接回车使用默认值: ").strip() or "教育综合（通用）"
    primary_price = input("请输入规格1价格，直接回车使用默认值: ").strip() or "8.9"
    secondary_spec_name = input("请输入规格2名称，直接回车使用默认值: ").strip() or "专业知识+教育综合"
    secondary_price = input("请输入规格2价格，直接回车使用默认值: ").strip() or "17.9"

    return StartupDefaults(
        excel_path=excel_path,
        primary_spec_name=primary_spec_name,
        primary_price=primary_price,
        secondary_spec_name=secondary_spec_name,
        secondary_price=secondary_price,
        stock=200,
        start_url="https://www.goofish.com/",
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    defaults = collect_startup_defaults() if args.excel is None else StartupDefaults(excel_path=args.excel)
    excel_path = defaults.excel_path
    if excel_path is None:
        print("没有可用的 Excel 文件。")
        return 1

    logger, log_path = build_run_logger(Path("logs"))
    print(f"运行日志: {log_path}")

    with sync_playwright() as playwright:
        browser, page = connect_xianyu_page(playwright)
        publisher = XianyuPublisher(page=page)

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

        summary = run_publish_batch(excel_path=excel_path, publisher=publisher, runtime_factory=runtime_factory)
        print(f"完成：成功 {summary.success_count}，失败 {summary.failure_count}，跳过 {summary.skipped_count}")
        log_info = getattr(logger, "info", None)
        if callable(log_info):
            log_info(
                "batch finished: success=%s failure=%s skipped=%s",
                summary.success_count,
                summary.failure_count,
                summary.skipped_count,
            )
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
