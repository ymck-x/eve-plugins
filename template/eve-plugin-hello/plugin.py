"""最小插件模板：复制这个目录，改 NAME / 工具名 / _run 里的实现即可。"""
from eve_app.plugins import define_tool

NAME = "hello"
INJECT = ("tools",)
CONFIG = {}
PERMISSIONS = ()


def _run(ctx, args, exec=None):
    who = str((args or {}).get("who") or "你")
    return {"ok": True, "text": f"你好，{who}！"}


def apply(ctx, config):
    ctx.tools.register(define_tool(
        name="hello_say",
        description="对一个人说你好",
        parameters={
            "type": "object",
            "properties": {"who": {"type": "string", "description": "对谁说"}},
            "additionalProperties": False,
        },
        output={"type": "object"},
        execute=_run,
    ))


def dispose(ctx):
    ctx.tools.unregister("hello_say")
