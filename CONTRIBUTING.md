# 提交插件到官方库

## 收什么

- **官方能力包**：团队自己写、随 EVE 发布的那 13 个（`plugins/eve-plugin-<id>/`）。
- **社区插件**：独立仓库，在 `registry.json` 里加一条，走 PR 评审。

不收：改人格 / 声音 / 核心记忆的包；静默采集摄像头 / 麦克风 / 屏幕的包；把用户数据打包出去的包；混淆代码或下载后再执行的包。

## 流程

1. 插件放成 `eve-plugin-<id>/`（官方包放本仓 `plugins/` 下，社区插件放自己的仓库）。
2. 按 [docs/plugin-format.md](docs/plugin-format.md) 写全包：`pyproject.toml` + `eve-plugin.yaml` + 七个入口名 + 离线测试。
3. `eve plugin check <path>` 全绿。
4. 在 `registry.json` 的 `plugins` 里加一条（格式见 [docs/registry-format.md](docs/registry-format.md)），并在 README 的能力表里补一行。
5. 开 PR，标题：`plugin: add <id>@<version>`。
6. 自动扫描 + 人工抽检。通过 → `verified: true` + `verified_version`；不通过 → 只按「未验证」可装，或直接拒收。

## 审核清单

- [ ] `eve-plugin.yaml` 字段齐全，`eve_api` 与当前稳定线兼容，版本与 `pyproject.toml` 一致。
- [ ] 入口只导出七个名字；`apply` 幂等、不阻塞；`dispose` 清干净。
- [ ] `permissions` 与代码实际行为一致，没有多要。
- [ ] 没有 postinstall / 动态下载代码；安装前不执行包代码。
- [ ] `eve plugin check` 14 项全绿；测试不调真实付费 API、不写用户数据。
- [ ] 高风险权限（支付、读全盘、执行命令）单独说明，并在运行时逐次确认。
- [ ] 插件不直接对用户说话：只返回结果 / 事实 / 动作，话由 EVE 说。
- [ ] 卸载时能清的都清（注册、子进程、后台任务）；数据保留还是删除要问。

## 版本更新

- 改 `version` 必须重新扫描、重新判定「已验证」。
- 权限变多 → 用户重新弹权限单，不继承。
- 高危权限不允许在补丁版本里悄悄加。
