# EVE 官方插件库

> 这里放两样东西：机器可读的插件索引 `registry.json`，以及官方插件包源码 `plugins/`。
> 插件契约（包结构 / 权限 / 信任分级 / 安装流程）以 EVE 主仓的插件设计稿为准；本仓库 `docs/` 是面向贡献者的公开口径。

## 两条路（先看这个）

- **你自己写**：复制 `template/eve-plugin-hello/`，改 `plugin.py` 里的一个函数，跑
  `python scripts\plugin_check.py <目录>`，再对 EVE 说「装这个插件 <目录>」。
- **让 EVE 写**：直接说「帮我写个插件：……」，她生成、检查、装；你只答信任和权限。
- **装现成的 MCP**：直接说「装 @modelcontextprotocol/server-memory」；没有 `eve-plugin.yaml` 也行，EVE 会按 `package.json` 自动生成清单、只装依赖、测协议。
- **拖进来**：把插件打成一个 `.zip` 拖到聊天输入框，发一句「装这个插件」；EVE 解包、检查、问权限。

不管谁写，装的时候都要你点头；EVE 不替你做这个决定。
## 这是什么

EVE 默认是一个完整的人：人格、声音、记忆、身体、感官都在本体里。能力则是一柜子可插拔的包。这个仓库是这些包的**官方来源**：

- **官方插件库**：EVE 先读根目录的 `registry.json` 找官方能力；离线时用本地缓存。
- **官方插件包**：`plugins/eve-plugin-<id>/`，一个包一个目录，带 `eve-plugin.yaml`、入口、离线测试。
- **第三方 / 用户插件不进这个仓库**：给 GitHub URL 或 npm 包名直接装，默认按「未验证」处理；想进官方库，走 PR（见 [CONTRIBUTING.md](CONTRIBUTING.md)）。

## 仓库结构

```
registry.json            # 机器可读索引，EVE 读这个
docs/registry-format.md  # 索引条目字段与规则
docs/plugin-format.md    # 插件包结构、七个入口名、eve-plugin.yaml、check 清单
docs/ai-authoring.md     # 让 DeepSeek / ChatGPT 等外部 AI 写插件的复制提示词
CONTRIBUTING.md          # 怎么提交、审什么
plugins/                 # 官方插件包源码，plugins/eve-plugin-<id>/
```

## registry.json

```json
{
  "schema": 1,
  "name": "EVE 官方插件库",
  "updated": "2026-11-06",
  "plugins": []
}
```

一个条目长这样：

```json
{
  "id": "lookup",
  "name": "查",
  "description": "联网搜索、读知识卡",
  "version": "0.1.0",
  "eve_api": ">=1.0 <2.0",
  "kind": "tool",
  "repo": "ymck-x/eve-plugins",
  "path": "plugins/eve-plugin-lookup",
  "entry": "eve_plugin_lookup",
  "permissions": ["network:https", "data:knowledge"],
  "risk": "medium",
  "verified": false,
  "verified_version": "",
  "signature": ""
}
```

字段、类型、必填项见 [docs/registry-format.md](docs/registry-format.md)。

## 插件怎么写

三种来源（官方 / EVE 自己写 / 用户写）用同一套结构，只改信任档与审核。一个包长这样：

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

三条铁律：

1. **入口只导出七个名字**；不搞魔法默认导出。
2. **`apply` 只注册，`dispose` 必清理**；import 零副作用、零阻塞。
3. **权限先声明，核心才放行**；插件不能自己给自己加权限。

本仓库的多包布局是 `plugins/eve-plugin-<id>/`。完整字段、`eve-plugin.yaml` 写法、`eve plugin check` 14 项见 [docs/plugin-format.md](docs/plugin-format.md)。

## 官方能力包（10 个）

出厂预设，随 EVE 发布，默认开（个别默认关），用户可随时关：

| # | 包 | 干什么 | 默认 |
|---|---|---|---|
| 1 | 查 | 联网搜索、知识卡 | 开 |
| 2 | 生活助理 | 日程提醒、自动化 | 开 |
| 3 | 购物 | 清单、比价、下单前确认 | 开 |
| 4 | 邮件 | 收发、草稿确认 | 开 |
| 5 | 办公 | 文档、表格、演示、PDF | 开 |
| 6 | 口语陪练 | 跟读、纠音 | 开 |
| 7 | 陪写作业 | 讲题、检查 | 关 |
| 8 | 投资 | 行情、持仓、盯价 | 关 |
| 9 | 家庭守护 | 用药提醒、跌倒、紧急联系人 | 开 |
| 10 | 工作台 | 编程 / 文档 / 研究长任务 | 开 |
| 11 | 多语言 | zh / en / ja / ko / es / fr | 开 |
| 12 | 答题格式 | 计数、当前值的结构化作答 | 开 |
| 13 | 首次认识 | 认主、建档 | 开 |

> 目前索引里还没有条目：第一批官方包随插件系统「阶段 1」迁入 `plugins/` 后再登记。在那之前，EVE 找新能力会退到 `web_search` 找候选。

## 安装来源

EVE 的安装器支持四种入口：官方库条目、用户自己的 GitHub 仓库 URL、npm 包、本地路径。这个仓库只负责第一种；其余三种由用户主动给出地址，默认按「未验证」处理。

## 信任与验证

| 档 | 谁 | 运行 | 默认 |
|---|---|---|---|
| 官方 | 团队签名 | 进程内 | 开 |
| 已验证 | 自动扫描 + 人工抽检 | 子进程沙箱 | 关，用户开 |
| 未验证 | 只扫描过 / 无签名 | 子进程沙箱 + 强警告 | 关，用户开 |
| 完全信任 | 用户明确选择 | 同进程，告知「和 EVE 同权限」 | 关，仅高级 |

- 「已验证」是**包 + 版本**的状态；换版本重新扫描、重新判定。
- 默认禁用安装脚本（postinstall 不跑）；安装前只读 manifest，不执行包代码。
- 新版本多要一项权限 → 重新弹权限单，不继承。

## 版本与兼容

条目用 `eve_api` 声明兼容范围；核心拒绝不兼容版本。稳定 API 至少支持 2 个 minor 版本（约 6–12 个月），弃用提前一个 minor 通知。

## 许可

**尚未设置 LICENSE。** 在确定许可之前，不要把这些文件当作可再分发的代码；官方插件包的许可会随每个包单独声明。
