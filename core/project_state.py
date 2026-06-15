from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import DefaultsPayload


class ProjectStateStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> DefaultsPayload:
        payload = DefaultsPayload()
        if not self.path.exists():
            return payload

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        for section_name, section_value in raw.items():
            if not hasattr(payload, section_name) or not isinstance(section_value, dict):
                continue
            section = getattr(payload, section_name)
            for key, value in section_value.items():
                if hasattr(section, key):
                    setattr(section, key, value)
        return payload

    def save(self, payload: DefaultsPayload) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
