from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_START_URL = "https://www.goofish.com/"
DEFAULT_PRIMARY_SPEC_NAME = "教育综合（通用）"
DEFAULT_PRIMARY_PRICE = "8.9"
DEFAULT_SECONDARY_SPEC_NAME = "专业知识+教育综合"
DEFAULT_SECONDARY_PRICE = "17.9"
DEFAULT_STOCK = 200
DEFAULT_CATEGORY_TEXT = "电子资料"
DEFAULT_24H_SHIPPING_TEXT = "24小时发货"
DEFAULT_NO_MAIL_TEXT = "无需邮寄"


@dataclass(frozen=True)
class StartupDefaults:
    excel_path: Path | None = None
    primary_spec_name: str = DEFAULT_PRIMARY_SPEC_NAME
    primary_price: str = DEFAULT_PRIMARY_PRICE
    secondary_spec_name: str = DEFAULT_SECONDARY_SPEC_NAME
    secondary_price: str = DEFAULT_SECONDARY_PRICE
    stock: int = DEFAULT_STOCK
    start_url: str = DEFAULT_START_URL
