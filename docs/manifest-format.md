# 插件 manifest 格式

> 状态：契约 v1（2026-11-06）。
> manifest 是安装前**唯一**被读取的文件；安装前不执行任何包代码。

## 文件位置

- 单包仓库：仓库根 `manifest.json`
- 本仓库多包：`plugins/<id>/manifest.json`

## 字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 唯一标识，kebab-case，与 `registry.json` 条目一致 |
| `name` | string | 是 | 显示名 |
| `version` | string | 是 | 插件版本，semver |
| `eve_api` | string | 是 | 兼容的 EVE 插件 API 范围 |
| `kind` | string | 是 | `tool` / `service` / `event`（人格 / 声音不走插件） |
| `entry` | string | 是 | 入口（Python 模块 / 子进程命令） |
| `permissions` | array | 是 | 权限清单，逐项对应代码实际行为 |
| `risk` | string | 是 | `low` / `medium` / `high` |
| `budget` | object | 是 | 每日 token / 金额 / 时间 / 调用频率上限 |
| `data_dir` | string | 否 | 插件自己的数据目录（相对数据根） |
| `signature` | string | 否 | 作者 / 官方签名；没有签名按未验证 |

## 权限怎么写

按权限组写，一项一行，只写真正用到的：

| 组 | 写法示例 |
|---|---|
| 记忆 | `memory:read` / `memory:write` |
| 人物 | `people` |
| 设备 | `device:camera` / `device:mic` / `device:screen` / `device:clipboard` |
| 数据 | `data:files` |
| 网络 | `network:https` |
| 动作 | `action:message` / `action:email` / `action:purchase` / `action:schedule` |
| 系统 | `system:exec` |
| 资源 | `resource:budget` |

> 精确枚举在第一批官方包落地时定稿；在那之前按上表写，评审按实际行为核对。

## 例子

```json
{
  "id": "lookup",
  "name": "查",
  "version": "0.1.0",
  "eve_api": ">=1.0 <2.0",
  "kind": "tool",
  "entry": "packages.lookup",
  "permissions": ["network:https", "data:knowledge"],
  "risk": "medium",
  "budget": {"calls_per_minute": 6, "calls_per_turn": 2, "results_per_call": 5},
  "data_dir": "knowledge",
  "signature": ""
}
```
