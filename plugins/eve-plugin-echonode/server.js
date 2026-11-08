/**
 * 零依赖 MCP 服务器示例：EVE 用 stdio 说话，一行一个 JSON-RPC。
 * 这是「用户自己会写 Node，就能写 EVE 插件」的最小样子。
 */
import { createInterface } from "node:readline";

const VERSION = "0.1.0";

function reply(id, result) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, result }) + "\n");
}

const rl = createInterface({ input: process.stdin });
rl.on("line", (line) => {
  if (!line.trim()) return;
  let msg;
  try {
    msg = JSON.parse(line);
  } catch {
    return;
  }
  const { id, method, params } = msg;
  if (id === undefined || id === null) return; // 通知不用回

  if (method === "initialize") {
    reply(id, {
      protocolVersion: params?.protocolVersion || "2025-06-18",
      capabilities: { tools: {} },
      serverInfo: { name: "eve-echonode", version: VERSION },
    });
  } else if (method === "tools/list") {
    reply(id, {
      tools: [
        {
          name: "echo_node",
          description: "把一段文字原样回显（Node 零依赖示例）。",
          inputSchema: {
            type: "object",
            properties: { text: { type: "string", description: "要回显的文字" } },
            required: ["text"],
          },
        },
      ],
    });
  } else if (method === "tools/call") {
    const text = String(params?.arguments?.text ?? "");
    reply(id, { content: [{ type: "text", text }] });
  } else if (method === "shutdown") {
    reply(id, {});
    rl.close();
    process.exit(0);
  } else {
    reply(id, {});
  }
});
