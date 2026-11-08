"""字数插件：数一段文字的字数、中文字数、英文词数，并记累计统计。

入口只导出 §17.2 的名字：NAME / INJECT / CONFIG / PERMISSIONS / apply / dispose。
跑法：`.venv\\Scripts\\python.exe scripts\\plugin_check.py plugins/eve-plugin-wordcount`
"""
from __future__ import annotations

import json
import re
from datetime import datetime

from eve_app.plugins import define_tool

NAME = "wordcount"
INJECT = ("tools", "data")
CONFIG = {}
PERMISSIONS = ("data:wordcount",)

_CJK = re.compile(r"[\u4e00-\u9fff]")
_WORD = re.compile(r"[A-Za-z0-9_]+")


def _count(text: str) -> dict:
    body = str(text or "")
    return {
        "chars": len(body),
        "chinese": len(_CJK.findall(body)),
        "words": len(_WORD.findall(body)),
        "lines": body.count("\n") + (1 if body else 0),
    }


def _stats_path(ctx):
    return ctx.data.dir() / "stats.json"


def _read_stats(ctx) -> dict:
    try:
        raw = ctx.data.read_json("stats.json")
    except Exception:  # noqa: BLE001 —— 统计坏了不影响数数
        return {"calls": 0, "chars": 0, "since": None}
    if not isinstance(raw, dict):
        return {"calls": 0, "chars": 0, "since": None}
    return {
        "calls": int(raw.get("calls") or 0),
        "chars": int(raw.get("chars") or 0),
        "since": raw.get("since"),
    }


def _bump(ctx, counted: dict) -> dict:
    stats = _read_stats(ctx)
    stats["calls"] += 1
    stats["chars"] += int(counted["chars"])
    stats["since"] = stats["since"] or datetime.now().isoformat(timespec="seconds")
    try:
        ctx.data.atomic_write_json("stats.json", stats)
    except Exception:  # noqa: BLE001 —— 记账失败不许让这一轮失败
        pass
    return stats


def _word_count(ctx, args, exec=None):
    counted = _count(str((args or {}).get("text") or ""))
    stats = _bump(ctx, counted)
    counted["total_calls"] = stats["calls"]
    counted["total_chars"] = stats["chars"]
    return counted


def _wordcount_stats(ctx, args, exec=None):
    stats = _read_stats(ctx)
    stats["since"] = stats.get("since") or ""
    return stats


def apply(ctx, config):
    ctx.tools.register(define_tool(
        name="word_count",
        description="数一段文字的字数：中文字数、英文词数、行数，并累计统计。",
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要数的文字"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
        output={"type": "object"},
        execute=_word_count,
    ))
    ctx.tools.register(define_tool(
        name="wordcount_stats",
        description="看字数插件记下的累计统计（调用次数 / 累计字数 / 从什么时候开始）。",
        parameters={"type": "object", "properties": {}, "additionalProperties": False},
        output={"type": "object"},
        execute=_wordcount_stats,
    ))


def dispose(ctx):
    ctx.tools.unregister("word_count")
    ctx.tools.unregister("wordcount_stats")
