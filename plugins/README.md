# plugins/

官方插件包放这里，一个包一个目录：`plugins/eve-plugin-<id>/`。

当前状态：**空**。第一批 13 个官方能力包随插件系统「阶段 1」迁入；迁入之前，`registry.json` 里不会有条目。

每个包至少要有：

- `pyproject.toml`
- `eve-plugin.yaml`（manifest，格式见 [../docs/plugin-format.md](../docs/plugin-format.md)）
- `eve_plugin_<id>/__init__.py`：只导出七个名字（`NAME` / `INJECT` / `OPTIONAL_INJECT` / `CONFIG` / `PERMISSIONS` / `apply` / `dispose`）
- `tests/`：离线测试，不调真实 API、不写用户数据
- `README.md`：做什么、要什么权限、怎么关

包与包之间不互相 import；共享逻辑走核心 API，不要复制一份核心实现。
