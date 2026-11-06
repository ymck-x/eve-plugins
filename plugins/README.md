# plugins/

官方插件包放这里，一个包一个目录：`plugins/<id>/`。

当前状态：**空**。第一批 13 个官方能力包随插件系统「阶段 1」迁入；迁入之前，`registry.json` 里不会有条目。

每个包至少要有：

- `manifest.json`（格式见 [../docs/manifest-format.md](../docs/manifest-format.md)）
- 入口（Python 模块或子进程命令）
- 自己的测试（不调真实 API、不写用户数据）
- 一份人话说明：做什么、要什么权限、怎么关

包与包之间不互相 import；共享逻辑走核心 API，不要复制一份核心实现。
