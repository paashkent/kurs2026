import json
from pathlib import Path
from typing import Any


class JsonStorage:
    """Простое JSON-хранилище для учебного проекта."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.save({"products": [], "users": [], "orders": []})

    def load(self) -> dict[str, Any]:
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"products": [], "users": [], "orders": []}

    def save(self, data: dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
