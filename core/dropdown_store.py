# -*- coding: utf-8 -*-
"""Load and serve dropdown options from dropdowns.json."""
import json
import os
from typing import Any, Dict, List


class DropdownStore:
    """管理下拉选项的存储。"""

    def __init__(self, filepath: str = None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, "dropdowns.json")
        self._filepath = filepath
        self._data: Dict[str, Dict[str, List[Any]]] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._filepath):
            with open(self._filepath, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def get_options(self, section: str, key: str) -> list:
        """获取某个 section 下某字段的下拉选项。"""
        return self._data.get(section, {}).get(key, [])

    def get_section_keys(self, section: str) -> dict:
        """获取某个 section 的全部选项。"""
        return self._data.get(section, {})

    def save(self) -> None:
        """保存回文件。"""
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def filepath(self) -> str:
        return self._filepath

    @property
    def data(self) -> dict:
        return self._data
