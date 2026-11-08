# 插件包格式：`eve-plugin-<id>`

> 状态：契约 v1（2026-11-06）。三种来源（官方 / EVE 自己写 / 用户写）用同一套结构，只改信任档与审核。

## 目录

```
eve-plugin-<id>/
  pyproject.toml          # Python 包：名、版本、依赖、入口
  eve-plugin.yaml         # manifest：安装器唯一读的
  eve_plugin_<id>/
    __init__.py           # NAME / INJECT / OPTIONAL_INJECT / CONFIG / PERMISSIONS / apply / dispose
    tools.py              # define_tool(...)
    contract.py           # 结果 schema / 错误码
  tests/                  # 离线测试
  README.md               # 什么时候用 / 权限 / 数据 / 例子
```

- `eve-plugin.yaml` 与 `pyproject.toml` 的版本必须一致（`python scripts\plugin_check.py` 校验）。
- 测试必须能离线跑；不调真实 API、不写真实数据。
- 本仓库的多包布局：`plugins/eve-plugin-<id>/`。

## 入口：只导出七个名字

```python
NAME = "lookup"
INJECT = ("tools", "audit")                 # 硬依赖：不在就不启动
OPTIONAL_INJECT = ("memory",)               # 有就用，没有也能跑
PERMISSIONS = ("network:https", "data:knowledge")
CONFIG = LookupConfig(max_results=5, backends=("bingrss", "ddgs", "360"))

def apply(ctx, config):
    ctx.tools.register(define_tool(...))

def dispose(ctx):
    ...  # 停任务、清注册、关连接
```

- Loader 只认这七个名字；不搞魔法默认导出。
- `apply` 只做注册；**不阻塞、import 时零副作用**；必须幂等。
- `dispose` 必须清干净：工具 / 事件 / 后台任务 / 连接 / 临时文件。
- `apply` 抛错 → 加载失败，不留半装。

## eve-plugin.yaml

| 字段 | 必填 | 规则 |
|---|---|---|
| `id` | 是 | kebab-case，唯一 |
| `name` | 是 | 显示名 |
| `version` | 是 | semver；与包版本一致 |
| `eve_api` | 是 | 兼容范围，如 `>=1.0 <2.0` |
| `kind` | 是 | `tool` / `service` / `event` |
| `entry` | Python 是；子进程否 | Python：入口文件或模块（如 `plugin.py` / `eve_plugin_lookup`） |
| `runtime` | 否 | `python`（默认）/ `jsonrpc` / `mcp` |
| `command` / `args` | 子进程是 | 启动命令（如 `["node", "server.js"]`） |
| `permissions` | 是（可为空） | 只能用核心词表；未知 → 拒收 |
| `risk` | 是 | `low` / `medium` / `high` |
| `budget` | 是（可为空 `{}`） | 只认 `per_turn` / `per_minute` / `per_day` |
| `default` | 是 | `true` / `false`（出厂预设） |
| `data_version` | 是 | 数据版本（默认 1；升高时迁移） |
| `signature` | 否 | 官方 / 已验证必填 |

例子：

```yaml
id: lookup
name: 查
version: 0.1.0
eve_api: ">=1.0 <2.0"
kind: [tool]
entry: eve_plugin_lookup
permissions:
  - network:https
  - data:knowledge
risk: medium
budget:
  per_minute: 6
  per_turn: 2
default: true
signature: ""
```

## Node / MCP 插件（不用 Python）

同一个清单，换成 `runtime` + `command`，包就是普通的 Node 工程：

```yaml
id: echo-node
name: 回显
version: 0.1.0
eve_api: ">=1.0 <2.0"
kind: [tool]
runtime: mcp
command: ["node", "server.js"]
args: []
permissions: []
risk: low
budget: {}
default: false
data_version: 1
```

- `server.js` 按 MCP stdio 协议实现 `initialize` / `tools/list` / `tools/call`（一行一个 JSON-RPC）；
- 不需要 `entry`，也不需要 `pyproject.toml`；
- `plugin_check` 对子进程 runtime 的 Python 专属项（import/apply/工具 schema/dispose）改由**安装事务的真协议测试**覆盖；安装时 EVE 会真起进程、列工具、调一次，再问你要不要装；
- 依赖：EVE 不跑 `npm install`，包要么零依赖，要么自己把依赖打进去。
## 现成的 npm MCP 包（没有清单也能装）

普通 MCP 包（例如 `@modelcontextprotocol/server-memory`）不需要作者写 `eve-plugin.yaml`：

- 只要 `package.json` 有 `bin` / `main`，EVE 按包名自动生成清单：`runtime: mcp`、`command: ["node", <bin>]`；
- 依赖由 EVE 在**用户信任后**用自带 npm 装：`install/ci --omit=dev --ignore-scripts`（不跑安装脚本，240s 超时、500MB 上限）；
- 装完先起真 MCP 协议测试（`initialize` → `tools/list`），再问权限；不是 MCP 的普通 npm 库会在这一步失败；
- 自动清单默认声明 `network:https`（MCP 服务多半要联网），用户可以在权限单里拒掉。
## 配置

- `CONFIG` 是 schema；必填无默认 → **加载时失败**。
- 先校验再 `apply`；非法配置拒收。
- 配置变更：重新 `apply` 或重载；不静默改全局。
- 密钥不进 config；从核心凭据服务读；日志不落密钥。

## 工具

- `define_tool(name, description, parameters, output, execute, timeout_ms, parallel_safe)`。
- `parameters` 用 JSON Schema；`additionalProperties: false`；执行前校验。
- `output` 声明 schema；只返回声明的 JSON；不返回 HTML / 原始字节（除非显式声明）。
- `execute` 异步；观察 `exec.signal`；不 print、不直接对用户说话、不阻塞事件循环；用 `ctx.logger` / 审计。
- 错误抛 `ToolError(code, message, user_message?)`；流水线转结构化错误；不泄漏堆栈 / 密钥。
- 工具名全局唯一；重复 → 拒收。

## 权限与数据

- manifest 声明；核心在 API 边界拦；未声明 → 运行时拒收。
- 高危（钱 / 消息 / 摄像头 / 麦克风 / 数据根外文件 / 执行命令）必须走 `ctx.approvals`；插件不能自己给自己加权限。
- 只写自己的 `<data_root>/plugins/<id>/`（`ctx.data.dir()`；`data_dir` 字段已废止，写了也忽略）；人的数据（身份 / 关系 / 偏好 / 日程 / 账本）走核心 API，不直接翻文件。
- 数据可导出、可删除；卸载时按用户选择保留 / 删除。
- 审计 / 日志不含用户原文、密钥、整页正文。

## 测试

- 单元测试 + 契约测试；假服务、假后端；不调真实 API / 网络 / 数据。
- `python scripts\plugin_check.py <path>`（在 EVE 仓库根目录）必须全绿才允许安装；官方 / EVE / 用户同一把尺。

### `plugin_check` 14 项

1. manifest 字段齐全、`eve_api` 合法、版本一致。
2. Python 包能 import，七个入口名字都在；子进程 runtime 的入口/工具由安装事务的真协议测试覆盖。
3. Python：`INJECT` / `OPTIONAL_INJECT` 的服务在当前运行时存在。
4. `CONFIG` 能校验；必填缺失 → 加载失败；默认值生效。
5. `apply` 幂等；不阻塞；import 无副作用。
6. Python：每个工具都有 name / description / parameters / output / execute；子进程：协议 `tools/list` 必须返回工具。
7. 参数、输出 schema、错误码都符合契约。
8. Python：`apply → dispose → apply` 能跑通，无残留；子进程：安装事务会重启/关闭进程验证无残留。
9. Python：`dispose` 清掉工具 / 事件 / 进程 / 连接；子进程：关闭走协议 `shutdown`，超时杀树。
10. 权限声明齐全；静态扫描 + 运行时拒收未声明；审计无密钥。
11. 测试离线全绿，且不调真实 API、不碰真实数据。
12. 能安装、启用、关闭、卸载；数据保留策略正确。
13. 第三方子进程崩溃 / 卡死 / 超时，核心不受影响。
14. 不能注册人格 / 声音 / 身体 / 感官命名空间；不能直接对用户说话；版本兼容检查通过。
