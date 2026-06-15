from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from .config import DEFAULT_24H_SHIPPING_TEXT, DEFAULT_CATEGORY_TEXT, DEFAULT_NO_MAIL_TEXT
from .models import PublishMaterials, PublishRuntimeConfig


class PublishNeedsManualReview(RuntimeError):
    pass


class XianyuPublisher:
    def __init__(self, page, *, sleep: Callable[[float], None] | None = None) -> None:
        self.page = page
        self._sleep = sleep or time.sleep
        self._session_origin_page = page
        self._session_pages: list = []
        self._session_known_pages: list = []

    def open(self, start_url: str) -> None:
        goto = getattr(self.page, "goto", None)
        if callable(goto):
            goto(start_url, wait_until="domcontentloaded")

    def publish(self, *, materials: PublishMaterials, runtime: PublishRuntimeConfig) -> None:
        self._begin_publish_session()
        try:
            self.open(runtime.start_url)
            self._click_publish_entry()
            self._upload_main_image(materials.main_image)
            if materials.detail_images:
                self._upload_detail_images(materials.detail_images)
            self._fill_content(runtime.content)
            self._ensure_category(DEFAULT_CATEGORY_TEXT)
            self._fill_specs(runtime)
            self._set_shipping_flags()
            self._select_location(runtime.location)
            self._submit()
            self._wait_for_success()
        finally:
            self._finish_publish_session()

    def _record(self, *action) -> None:
        if hasattr(self.page, "actions"):
            self.page.actions.append(action)

    def _is_fake_page(self) -> bool:
        return hasattr(self.page, "actions")

    def _begin_publish_session(self) -> None:
        self._session_origin_page = self.page
        self._session_pages = []
        context = getattr(self.page, "context", None)
        context_pages = getattr(context, "pages", None)
        self._session_known_pages = list(context_pages) if context_pages else [self.page]

    def _finish_publish_session(self) -> None:
        for page in list(self._session_pages):
            if page is self._session_origin_page:
                continue
            try:
                is_closed = getattr(page, "is_closed", None)
                if callable(is_closed) and is_closed():
                    continue
            except Exception:  # noqa: BLE001
                pass
            close = getattr(page, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:  # noqa: BLE001
                    pass
        self.page = self._session_origin_page
        self._session_pages = []
        self._session_known_pages = []

    def _remember_session_page(self, page) -> None:
        if page is None or page is self._session_origin_page:
            return
        if any(existing is page for existing in self._session_pages):
            return
        self._session_pages.append(page)

    def _click_publish_entry(self) -> None:
        if self._is_fake_page():
            self._record("click_publish_entry")
            return
        popup_page = self._open_sidebar_publish_page()
        if popup_page is not None:
            self.page = popup_page
            self._pause()
            return
        self._click_text("发闲置")
        self._pause()

    def _open_sidebar_publish_page(self):
        try:
            locator = self.page.locator("[class*='sidebar-container'] a:has-text('发闲置')")
            if locator.count() == 0:
                return None
            trigger = locator.first
            href = trigger.get_attribute("href")
            target = trigger.get_attribute("target")
            context = getattr(self.page, "context", None)

            if href and target == "_blank" and context is not None:
                try:
                    with context.expect_page(timeout=10000) as new_page_info:
                        trigger.click(timeout=5000)
                    popup_page = new_page_info.value
                    popup_page.wait_for_load_state("domcontentloaded", timeout=15000)
                    self._remember_session_page(popup_page)
                    return popup_page
                except Exception:  # noqa: BLE001
                    goto = getattr(self.page, "goto", None)
                    if callable(goto):
                        goto(href, wait_until="domcontentloaded")
                        return self.page
                    return None

            trigger.click(timeout=5000)
            return self.page
        except Exception:  # noqa: BLE001
            return None

    def _upload_main_image(self, path: Path) -> None:
        if self._is_fake_page():
            self._record("upload_main", path.name)
            return
        self._upload_files(("添加首图", "上传首图"), [path])
        self._pause(long=True)

    def _upload_detail_images(self, paths: tuple[Path, ...]) -> None:
        if self._is_fake_page():
            self._record("upload_detail", tuple(path.name for path in paths))
            return
        self._upload_files(("添加细节图", "添加详情图"), list(paths))
        self._pause(long=True)

    def _fill_content(self, content: str) -> None:
        if self._is_fake_page():
            self._record("fill_content", content)
            return
        normalized_content = self._normalize_multiline_text(content)
        textarea = self.page.locator("textarea")
        try:
            if textarea.count() > 0:
                textarea.first.fill(normalized_content, timeout=5000)
                self._pause()
                return
        except Exception:  # noqa: BLE001
            pass
        for locator in (
            self.page.locator("[contenteditable='true']"),
            self.page.get_by_placeholder("宝贝描述"),
            self.page.get_by_role("textbox", name="宝贝描述"),
        ):
            try:
                if locator.count() == 0:
                    continue
                self._fill_contenteditable(locator.first, normalized_content)
                self._pause()
                return
            except Exception:  # noqa: BLE001
                continue
        raise RuntimeError("没有找到宝贝描述输入框")

    def _fill_contenteditable(self, locator, content: str) -> None:
        keyboard = getattr(self.page, "keyboard", None)
        if keyboard is None:
            raise RuntimeError("当前页面不支持键盘输入")
        locator.click(timeout=5000)
        locator.press("Control+A", timeout=5000)
        keyboard.press("Backspace")
        lines = content.split("\n")
        for index, line in enumerate(lines):
            if line:
                keyboard.insert_text(line)
            if index < len(lines) - 1:
                keyboard.press("Shift+Enter")

    def _normalize_multiline_text(self, content: str) -> str:
        return content.replace("\r\n", "\n").replace("\r", "\n")

    def _ensure_category(self, category_text: str) -> None:
        if self._is_fake_page():
            self._record("ensure_category", category_text)
            return
        try:
            if self.page.get_by_text(category_text, exact=False).count() > 0:
                return
        except Exception:  # noqa: BLE001
            pass
        self._click_text("分类")
        self._pause()
        self._click_text(category_text)
        self._pause()

    def _fill_specs(self, runtime: PublishRuntimeConfig) -> None:
        if self._is_fake_page():
            for index, spec in enumerate(runtime.specs):
                self._record("fill_spec_name", index, spec.name)
                self._record("fill_spec_price", index, spec.price)
                self._record("fill_spec_stock", index, str(spec.stock))
            return
        if self._uses_dynamic_spec_builder():
            self._fill_dynamic_specs(runtime)
            return
        for index, spec in enumerate(runtime.specs):
            self._fill_nth_input(("请输入具体的规格", "规格"), index, spec.name)
            self._fill_nth_input(("价格",), index, spec.price)
            self._fill_nth_input(("库存",), index, str(spec.stock))
            self._pause()

    def _uses_dynamic_spec_builder(self) -> bool:
        try:
            return self.page.locator("button:has-text('添加规格类型')").count() > 0
        except Exception:  # noqa: BLE001
            return False

    def _fill_dynamic_specs(self, runtime: PublishRuntimeConfig) -> None:
        add_button = self.page.locator("button:has-text('添加规格类型')")
        if add_button.count() == 0:
            raise RuntimeError("没有找到规格类型入口")
        add_button.first.click(timeout=5000)
        self._pause()

        spec_type_input = self._wait_for_locator_count(
            "input[id$='_propertyName']",
            1,
            error_message="没有找到规格类型输入框",
        )
        selector = spec_type_input.first.locator("xpath=ancestor::div[contains(@class,'ant-select-selector')][1]")
        if selector.count() == 0:
            raise RuntimeError("没有找到规格类型选择框")
        selector_box = selector.first
        try:
            current_text = selector_box.inner_text(timeout=1000)
        except Exception:  # noqa: BLE001
            current_text = ""
        if "颜色" not in current_text:
            selector_box.click(timeout=5000)
            self._pause()
            spec_type_input.first.press("Enter", timeout=5000)
            self._pause()

        for index, spec in enumerate(runtime.specs):
            value_inputs = self._wait_for_locator_count(
                "input[class*='propertyValueInput']",
                index + 1,
                error_message="没有生成规格值输入框",
            )
            value_input = value_inputs.nth(index)
            value_input.fill(spec.name, timeout=5000)
            value_input.press("Enter", timeout=5000)
            self._pause()

        price_inputs = self._wait_for_locator_count(
            "input[placeholder='0.00']",
            len(runtime.specs),
            error_message="没有生成规格价格输入框",
        )
        stock_inputs = self._wait_for_locator_count(
            "input[placeholder='0']",
            len(runtime.specs),
            error_message="没有生成规格库存输入框",
        )

        for index, spec in enumerate(runtime.specs):
            price_inputs.nth(index).fill(spec.price, timeout=5000)
            stock_inputs.nth(index).fill(str(spec.stock), timeout=5000)
            self._pause()

    def _set_shipping_flags(self) -> None:
        if self._is_fake_page():
            self._record("set_shipping_flags", DEFAULT_24H_SHIPPING_TEXT, DEFAULT_NO_MAIL_TEXT)
            return
        self._ensure_toggle(DEFAULT_24H_SHIPPING_TEXT)
        self._ensure_toggle(DEFAULT_NO_MAIL_TEXT)
        self._pause()

    def _select_location(self, location: str) -> None:
        if self._is_fake_page():
            self._record("select_location", location)
            return
        try:
            opened = False
            for locator in (
                self.page.locator("[class*='addressWrap']"),
                self.page.locator("label[for='itemAddrDTO']"),
            ):
                try:
                    if locator.count() > 0:
                        locator.first.click(timeout=5000)
                        opened = True
                        break
                except Exception:  # noqa: BLE001
                    continue
            if not opened:
                self._click_text("宝贝所在地")
            self._pause()
            self._fill_first_available_locator(
                (
                    self.page.locator("input#search-input"),
                    self.page.get_by_placeholder("搜索地点"),
                    self.page.get_by_role("textbox", name="搜索地点"),
                ),
                location,
            )
            try:
                self._click_first_visible_text(exact=True, candidates=(location,))
            except RuntimeError:
                self._click_first_visible_text(exact=False, candidates=(location, "市", "区"))
            self._pause()
        except Exception:  # noqa: BLE001
            # 发货地是 best-effort，匹配失败时保留默认地址继续发布
            return

    def _submit(self) -> None:
        if self._is_fake_page():
            self._record("submit")
            return
        try:
            button = self.page.locator("button[class*='publish-button']")
            if button.count() > 0:
                publish_button = button.first
                class_name = publish_button.get_attribute("class") or ""
                disabled_attr = publish_button.get_attribute("disabled")
                is_enabled = getattr(publish_button, "is_enabled", None)
                if disabled_attr is not None or "disabled" in class_name or (callable(is_enabled) and not is_enabled()):
                    raise RuntimeError("发布按钮仍未就绪")
                try:
                    publish_button.click(timeout=5000)
                except Exception:
                    self._reset_submit_focus()
                    publish_button.click(timeout=5000)
            else:
                self._click_text("发布")
        except RuntimeError as exc:
            message = str(exc)
            if message == "没有找到按钮或文本: 发布":
                raise PublishNeedsManualReview("平台异常：发布按钮未正常出现，请人工确认是否已发布") from exc
            raise
        except Exception as exc:  # noqa: BLE001
            raise PublishNeedsManualReview("平台异常：发布按钮未正常出现，请人工确认是否已发布") from exc
        self._pause()

    def _reset_submit_focus(self) -> None:
        try:
            self.page.locator("body").first.click(position={"x": 20, "y": 20}, timeout=3000)
        except Exception:  # noqa: BLE001
            pass
        keyboard = getattr(self.page, "keyboard", None)
        if keyboard is None:
            return
        for key in ("Escape", "Tab"):
            try:
                keyboard.press(key)
            except Exception:  # noqa: BLE001
                continue

    def _wait_for_success(self) -> None:
        if self._is_fake_page():
            self._record("wait_for_success")
            return
        for _ in range(15):
            item_page = self._find_published_item_page()
            if item_page is not None:
                self._remember_session_page(item_page)
                self.page = item_page
                return
            for text in ("发布成功", "您的宝贝已发布", "审核中"):
                try:
                    self.page.get_by_text(text, exact=False).first.wait_for(timeout=1000)
                    return
                except Exception:  # noqa: BLE001
                    continue
            self._sleep(1.0)
        raise RuntimeError("没有检测到发布成功提示")

    def _pause(self, *, long: bool = False) -> None:
        self._sleep(1.5 if not long else 3.0)

    def _wait_for_locator_count(self, selector: str, minimum_count: int, *, error_message: str):
        last_count = 0
        for attempt in range(10):
            locator = self.page.locator(selector)
            try:
                last_count = locator.count()
            except Exception:  # noqa: BLE001
                last_count = 0
            if last_count >= minimum_count:
                return locator
            if attempt < 9:
                self._sleep(0.3)
        raise RuntimeError(f"{error_message}，当前数量 {last_count}，期望至少 {minimum_count}")

    def _click_text(self, text: str) -> None:
        for locator in (
            self.page.get_by_role("button", name=text),
            self.page.get_by_role("link", name=text),
            self.page.get_by_text(text, exact=True),
            self.page.get_by_text(text, exact=False),
        ):
            try:
                locator.first.click(timeout=5000)
                return
            except Exception:  # noqa: BLE001
                continue
        raise RuntimeError(f"没有找到按钮或文本: {text}")

    def _upload_files(self, trigger_texts: tuple[str, ...], paths: list[Path]) -> None:
        del trigger_texts
        try:
            file_input = self._wait_for_locator_count(
                "input[type='file']",
                1,
                error_message="没有找到图片上传入口",
            ).first
            file_input.set_input_files([str(path) for path in paths])
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("没有找到图片上传入口") from exc

    def _fill_nth_input(self, labels: tuple[str, ...], index: int, value: str) -> None:
        for label in labels:
            try:
                locator = self.page.get_by_placeholder(label)
                if locator.count() > index:
                    locator.nth(index).fill(value, timeout=5000)
                    return
            except Exception:  # noqa: BLE001
                continue
            try:
                locator = self.page.get_by_role("textbox", name=label)
                if locator.count() > index:
                    locator.nth(index).fill(value, timeout=5000)
                    return
            except Exception:  # noqa: BLE001
                continue

        try:
            inputs = self.page.locator("input")
            inputs.nth(index).fill(value, timeout=5000)
            return
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"没有找到可填写的输入框: {labels[0]}") from exc

    def _fill_first_available_locator(self, locators: tuple, value: str) -> None:
        for locator in locators:
            try:
                count = locator.count()
            except Exception:  # noqa: BLE001
                count = 0
            for index in range(count):
                try:
                    locator.nth(index).fill(value, timeout=5000)
                    self._pause()
                    return
                except Exception:  # noqa: BLE001
                    continue
        raise RuntimeError("没有找到可填写的搜索输入框")

    def _ensure_toggle(self, text: str) -> None:
        try:
            self._click_text(text)
        except RuntimeError:
            pass

    def _click_first_visible_text(self, *, exact: bool, candidates: tuple[str, ...]) -> None:
        last_error: Exception | None = None
        for candidate in candidates:
            try:
                locator = self.page.get_by_text(candidate, exact=exact)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue
            try:
                count = locator.count()
            except Exception as exc:  # noqa: BLE001
                try:
                    locator.first.click(timeout=5000)
                    return
                except Exception as fallback_exc:  # noqa: BLE001
                    last_error = fallback_exc
                    continue
            for index in range(count):
                try:
                    locator.nth(index).click(timeout=5000)
                    return
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
                    continue
        raise RuntimeError("没有找到可点击的目标文本") from last_error

    def _find_published_item_page(self):
        candidates = [self.page, *self._session_pages]
        context = getattr(self.page, "context", None)
        context_pages = getattr(context, "pages", None)
        if context_pages:
            for candidate in context_pages:
                if any(known is candidate for known in self._session_known_pages):
                    continue
                candidates.append(candidate)
        for candidate in candidates:
            url = getattr(candidate, "url", "") or ""
            if "/item?" in url or "/item?id=" in url:
                return candidate
        return None
