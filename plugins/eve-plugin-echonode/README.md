# 回显（Node 示例）

零依赖的 MCP 插件示例：把一段文字原样回显。用来演示「任何会写 Node 的人都能写 EVE 插件」。

## 安装

对 EVE 说：`装这个插件 <这个目录的绝对路径>`。EVE 会检查、问你信任、跑协议测试，然后装进子进程。

## 文件

- `eve-plugin.yaml`：清单（EVE 检查/安装时唯一读的东西）
- `server.js`：MCP 服务器（stdio，一行一个 JSON-RPC）
- `package.json`：普通 Node 包信息（零依赖）
