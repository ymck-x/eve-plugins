# 让别的 AI 写 EVE 插件（复制这段）

> 适用：DeepSeek / ChatGPT / Claude 等**不知道 EVE** 的模型。
> 用法：把下面「提示词」整段复制给它，最后一行换成你的需求；它输出文件后，
> 跑 `python scripts\plugin_check.py <目录>`，14 项全绿再让 EVE 装。
> 如果模型能联网，也可以只给它本仓库地址，让它先读 `docs/plugin-format.md`。
> 用 EVE 自己写则不需要这段——她内置这套规则（`plugin_scaffold`）。

---

## 提示词（从这里开始复制）

你要为一个叫 EVE 的助手写一个插件。EVE 是 Python 的，插件跑在它进程内。
**只输出文件，不要解释，不要输出多余的话。**

### 目录结构（必须完全一致）

```
eve-plugin-<id>/
  eve-plugin.yaml
  plugin.py
  pyproject.toml
  README.md
  tests/test_offline.py
```

`<id>` 只能是小写字母、数字、短横线，例如 `water-reminder`。

### eve-plugin.yaml（照这个写，只改值）

```yaml
id: water-reminder
name: 喝水提醒
description: 到点提醒喝水，并记下今天喝了几次
version: 0.1.0
eve_api: ">=1.0 <2.0"
kind: [tool]
entry: plugin.py
permissions: [data:water-reminder]
risk: low
budget: {}
default: false
data_version: 1
```

### plugin.py（只导出这些名字）

```python
from eve_app.plugins import define_tool

NAME = "water-reminder"
INJECT = ("tools", "data")
CONFIG = {}
PERMISSIONS = ("data:water-reminder",)


def _drink(ctx, args, exec=None):
    # 用 ctx.data 存自己的数据；不要读写别的目录
    try:
        state = ctx.data.read_json("state.json")
    except Exception:
        state = {}
    count = int(state.get("count") or 0) + 1
    ctx.data.atomic_write_json("state.json", {"count": count})
    return {"ok": True, "count": count}


def apply(ctx, config):
    ctx.tools.register(define_tool(
        name="water_drink",
        description="记一次喝水，返回今天第几次",
        parameters={"type": "object", "properties": {}, "additionalProperties": False},
        output={"type": "object"},
        execute=_drink,
    ))


def dispose(ctx):
    ctx.tools.unregister("water_drink")
```

### 必须遵守的规则

1. 只 `from eve_app.plugins import define_tool`；**不要 import EVE 核心的其它模块**。
2. `plugin.py` 只导出 `NAME / INJECT / CONFIG / PERMISSIONS / apply / dispose`；不要顶层执行代码、不要 `print`。
3. 每个工具用 `define_tool(name, description, parameters, output, execute)`；`parameters` 是 JSON Schema，必须写 `"additionalProperties": False`；`execute` 返回 JSON 可序列化的 dict。
4. 工具名只能字母/数字/下划线；不要和核心工具重名（`schedule_add`、`shopping_list`、`read_document` 等）。
5. 权限只能从这张表里选，且 `data:` 必须写 `data:<id>`：
   `data:<id>`、`memory:read`、`memory:write`、`network:https`、`web:interact`、
   `action:confirm`、`schedule:write`、`jobs:spawn`、`event:subscribe`、`event:emit`、
   `say:propose`、`ui:ask`、`ui:panel`、`system:exec`、`vision:read`、`service:<name>`。
   **用不到就不要声明**；多声明一项会被当成“权限单撒谎”拒收。
6. 不要用 `eval` / `exec` / `subprocess` / `socket` / 直接 `urllib`；不要碰人格、声音、摄像头、麦克风；不要读写数据目录以外的文件。
7. 数据只放 `ctx.data`（对应 `<data_root>/plugins/<id>/`）；**不要写 `data_dir` 字段**。
8. 测试必须离线：不联网、不调真实 API、不写真实数据。
9. `pyproject.toml` 的版本必须和 `eve-plugin.yaml` 一致（`0.1.0`）；README 用中文写“什么时候用 / 权限 / 例子”。

### 输出格式

每个文件用一行 `### 文件：<相对路径>`，紧接着一个代码块，例：

```
### 文件：eve-plugin-water-reminder/eve-plugin.yaml
```yaml
...
```
```

### 我的需求

（在这里写你要的插件：叫什么、干什么、什么时候用。）

---

## 写完以后

1. 把模型输出的文件按路径存好（每个包一个目录）；
2. 在 EVE 仓库根目录跑：
   `.venv\Scripts\python.exe scripts\plugin_check.py <包目录>`
   14 项全绿才算合格；红哪项就让它改哪项；
3. 对 EVE 说「装这个插件 <包目录的绝对路径>」；EVE 会再问信任、逐项过权限单，然后装。

**不要相信模型说“能跑”**——以 `plugin_check` 和 EVE 安装时的真协议测试为准。
