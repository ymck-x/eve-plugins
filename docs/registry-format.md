# registry.json 条目格式

> 状态：契约 v1（2026-11-06）。改字段前先开 issue：EVE 的核心直接读这个文件。

## 顶层

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `schema` | integer | 是 | 格式版本，目前固定 `1` |
| `name` | string | 是 | 库的显示名 |
| `updated` | string | 是 | 最后人工更新日期，`YYYY-MM-DD` |
| `plugins` | array | 是 | 条目列表；空数组合法（当前就是空） |

## 条目

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 全库唯一，kebab-case；官方包与 `eve-plugin-<id>` 目录名一致 |
| `name` | string | 是 | 显示名（能力目录里给人看的那一行） |
| `description` | string | 是 | 一句话「什么时候用」；进能力目录，不长讲 |
| `version` | string | 是 | semver（`0.1.0`） |
| `eve_api` | string | 是 | 兼容的 EVE 插件 API 范围（`>=1.0 <2.0`） |
| `kind` | string | 是 | `tool` / `service` / `event` |
| `repo` | string | 二选一 | `owner/name` |
| `path` | string | 否 | 单仓多包时的子目录（`plugins/eve-plugin-<id>`） |
| `npm` | string | 二选一 | npm 包名 |
| `entry` | string | 是 | 入口 Python 模块（如 `eve_plugin_lookup`） |
| `permissions` | array | 是 | 权限清单，只写实际用到的 |
| `risk` | string | 是 | `low` / `medium` / `high` |
| `verified` | boolean | 是 | 是否通过「包 + 版本」级抽检 |
| `verified_version` | string | 是 | 抽检通过的那个版本；与 `version` 不一致即按未验证 |
| `signature` | string | 否 | 签名来源（signed tag / commit / manifest 签名）；空 = 未验证 |

## 规则

1. `id` 全库唯一、kebab-case、不含空格；官方包的 `id` 与 `plugins/eve-plugin-<id>/` 目录名一致。
2. `repo` 和 `npm` 至少有一个。官方包用 `repo` + `path`（同一个仓库放多个包）。
3. `verified` 只有人工抽检通过才为 `true`；`verified_version` 必须等于当前 `version`，否则一律按未验证。
4. `permissions` 只写实际用到的；多要一项就是权限单撒谎，拒收。合法词表见 [plugin-format.md](plugin-format.md)。
5. `eve_api` 必须是合法 semver 范围，且与插件 `eve-plugin.yaml` 里的 `eve_api` 一致。
6. `default`（出厂默认开关）只写在 manifest 里，索引不重复声明。
7. 删除条目 = 从库里撤下；已安装的用户不受影响，但必须能随时关、随时卸。

## 示例

```json
{
  "schema": 1,
  "name": "EVE 官方插件库",
  "updated": "2026-11-06",
  "plugins": [
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
      "verified": true,
      "verified_version": "0.1.0",
      "signature": "signed tag v0.1.0"
    }
  ]
}
```

> 上面的条目只是格式示例，不代表 `lookup` 已经发布。
