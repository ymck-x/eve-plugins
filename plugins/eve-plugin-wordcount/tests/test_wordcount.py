"""字数插件离线测试（不联网、不写真实数据）。

跑法：在 EVE 仓库根目录
  .venv\\Scripts\\python.exe plugins\\eve-plugin-wordcount\\tests\\test_wordcount.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parents[2]))  # EVE 仓库根（本仓库在 plugins/ 下时）

failures = []


def check(name, cond, detail=""):
    print(("  ✓ " if cond else "  ✗ ") + name + ("" if cond else f"  ← {detail}"))
    if not cond:
        failures.append(name)


def main():
    import importlib.util

    manifest = json.loads("{}")
    yaml_path = ROOT / "eve-plugin.yaml"
    text = yaml_path.read_text(encoding="utf-8")
    check("manifest 有 id", "id: wordcount" in text)
    check("manifest 有 data 权限", "data:wordcount" in text)

    spec = importlib.util.spec_from_file_location(
        "eve_plugin_wordcount", ROOT / "eve_plugin_wordcount" / "__init__.py",
        submodule_search_locations=[str(ROOT / "eve_plugin_wordcount")],
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    counted = module._count("今天 weather 不错\n第二行")
    check("字数", counted["chars"] == len("今天 weather 不错\n第二行"), counted)
    check("中文字数", counted["chinese"] == 7, counted)
    check("英文词数", counted["words"] == 1, counted)
    check("行数", counted["lines"] == 2, counted)
    print()
    if failures:
        print("失败：", failures)
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
