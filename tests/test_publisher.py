from vendor.xianyu_uploader.publisher import XianyuPublisher


class _FakeKeyboard:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def insert_text(self, value: str) -> None:
        self.events.append(("insert_text", value))

    def press(self, key: str) -> None:
        self.events.append(("press", key))


class _FakeLocator:
    def __init__(self, page, *, kind: str, count: int = 1) -> None:
        self.page = page
        self.kind = kind
        self._count = count

    @property
    def first(self):
        return self

    def count(self) -> int:
        return self._count

    def _ensure_present(self) -> None:
        if self._count <= 0:
            raise RuntimeError(f"locator not found: {self.kind}")

    def fill(self, value: str, timeout: int = 0) -> None:
        self._ensure_present()
        self.page.events.append(("fill", self.kind, value, timeout))

    def click(self, timeout: int = 0) -> None:
        self._ensure_present()
        self.page.events.append(("click", self.kind, timeout))

    def press(self, key: str, timeout: int = 0) -> None:
        self._ensure_present()
        self.page.events.append(("locator_press", self.kind, key, timeout))


class _FakePage:
    def __init__(self) -> None:
        self.events: list[tuple] = []
        self.keyboard = _FakeKeyboard()

    def locator(self, selector: str) -> _FakeLocator:
        if selector == "textarea":
            return _FakeLocator(self, kind="textarea", count=0)
        if selector == "[contenteditable='true']":
            return _FakeLocator(self, kind="contenteditable", count=1)
        return _FakeLocator(self, kind=selector, count=0)

    def get_by_placeholder(self, text: str) -> _FakeLocator:
        return _FakeLocator(self, kind=f"placeholder:{text}", count=0)

    def get_by_role(self, role: str, name: str) -> _FakeLocator:
        return _FakeLocator(self, kind=f"role:{role}:{name}", count=0)


def test_fill_content_uses_paragraph_safe_input_for_contenteditable() -> None:
    page = _FakePage()
    publisher = XianyuPublisher(page=page, sleep=lambda _: None)

    publisher._fill_content("标题\n\n第一段\n第二段\n\n#标签")

    assert ("fill", "contenteditable", "标题\n\n第一段\n第二段\n\n#标签", 5000) not in page.events
    assert page.events[:2] == [
        ("click", "contenteditable", 5000),
        ("locator_press", "contenteditable", "Control+A", 5000),
    ]
    assert page.keyboard.events == [
        ("press", "Backspace"),
        ("insert_text", "标题"),
        ("press", "Shift+Enter"),
        ("press", "Shift+Enter"),
        ("insert_text", "第一段"),
        ("press", "Shift+Enter"),
        ("insert_text", "第二段"),
        ("press", "Shift+Enter"),
        ("press", "Shift+Enter"),
        ("insert_text", "#标签"),
    ]
