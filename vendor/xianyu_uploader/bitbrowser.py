from __future__ import annotations

import json
import subprocess
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BitBrowserSession:
    user_data_dir: Path
    devtools_port: int

    @property
    def cdp_endpoint_url(self) -> str:
        return f"http://127.0.0.1:{self.devtools_port}"


def discover_running_session() -> BitBrowserSession:
    script = r"""
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -eq 'BitBrowser.exe' -and $_.CommandLine -match '--user-data-dir=' -and $_.CommandLine -notmatch '--type=' } |
  Select-Object -First 1 -ExpandProperty CommandLine
"""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        check=True,
    )
    command_line = result.stdout.strip()
    if not command_line:
        raise RuntimeError("未找到已打开的 BitBrowser")

    marker = "--user-data-dir="
    start = command_line.find(marker)
    if start < 0:
        raise RuntimeError("BitBrowser 参数中缺少 user-data-dir")
    raw_path = command_line[start + len(marker) :].split(" ", 1)[0].strip('"')
    user_data_dir = Path(raw_path)
    devtools_file = user_data_dir / "DevToolsActivePort"
    if not devtools_file.exists():
        raise RuntimeError("BitBrowser 调试端口未就绪，请先打开对应窗口")
    lines = [line.strip() for line in devtools_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    return BitBrowserSession(user_data_dir=user_data_dir, devtools_port=int(lines[0]))


def connect_xianyu_page(playwright):
    session = discover_running_session()
    with urllib.request.urlopen(f"{session.cdp_endpoint_url}/json/version", timeout=5) as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("webSocketDebuggerUrl"):
        raise RuntimeError("BitBrowser 调试端口不可用")

    browser = playwright.chromium.connect_over_cdp(session.cdp_endpoint_url, timeout=20000)
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    page = context.pages[0] if context.pages else context.new_page()
    return browser, page
