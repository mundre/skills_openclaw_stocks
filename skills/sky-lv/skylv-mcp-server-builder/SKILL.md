---
name: "mcp-server-builder"
slug: skylv-mcp-server-builder
version: 1.0.2
description: MCP (Model Context Protocol) server builder. Scaffolds MCP servers, tools, and prompt templates from scratch. Triggers: mcp server, model context protocol, mcp tools.
author: SKY-lv
license: MIT-0
tags: [mcp, openclaw, agent]
keywords: mcp, server, protocol, scaffolding
triggers: mcp server builder
---

# MCP Server Builder

## 功能说明

构建 Model Context Protocol 服务器，扩展 AI 能力边界。

## MCP 协议概述

MCP 是 Anthropic 推出的 AI 模型上下文协议，让 AI 能调用外部工具和数据源。

## 项目结构

```
mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts          # 主入口
│   ├── tools/            # 工具定义
│   └── resources/         # 资源定义
└── tsconfig.json
```

## 完整实现

### 1. 初始化项目

```bash
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node ts-node
```

```json
// package.json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0",
    "zod": "^3.22.0"
  }
}
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src/**/*"]
}
```

### 2. 定义工具

```typescript
// src/tools/search.ts
import { z } from 'zod';

export const searchTool = {
  name: 'web_search',
  description: '搜索互联网获取最新信息',
  inputSchema: z.object({
    query: z.string().describe('搜索关键词'),
    limit: z.number().optional().default(5).describe('返回结果数量')
  }),

  async handler(args: { query: string; limit?: number }) {
    // 实际实现
    const results = await performSearch(args.query, args.limit || 5);
    return {
      content: results.map(r => ({
        type: 'text' as const,
        text: `标题: ${r.title}\n链接: ${r.url}\n摘要: ${r.snippet}`
      }))
    };
  }
};
```

### 3. 定义资源

```typescript
// src/resources/knowledge.ts
export const knowledgeResources = {
  uriPrefix: 'knowledge://',

  list: async () => [
    {
      uri: 'knowledge://docs/latest',
      name: '最新文档',
      description: '系统最新文档版本',
      mimeType: 'text/markdown'
    }
  ],

  read: async (uri: string) => {
    if (uri === 'knowledge://docs/latest') {
      return {
        contents: [{
          uri,
          mimeType: 'text/markdown',
          text: '# 最新文档\n\n...'
        }]
      };
    }
    throw new Error('Resource not found');
  }
};
```

### 4. 主入口

```typescript
// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

import { searchTool } from './tools/search.js';
import { knowledgeResources } from './resources/knowledge.js';

class MyMCPServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      { name: 'my-mcp-server', version: '1.0.0' },
      { capabilities: { tools: {}, resources: {} } }
    );

    this.setupToolHandlers();
    this.setupResourceHandlers();
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: searchTool.name,
          description: searchTool.description,
          inputSchema: searchTool.inputSchema
        }
      ]
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      if (name === 'web_search') {
        return await searchTool.handler(args as any);
      }
      
      throw new Error(`Unknown tool: ${name}`);
    });
  }

  private setupResourceHandlers() {
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: await knowledgeResources.list()
    }));

    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      return await knowledgeResources.read(request.params.uri);
    });
  }

  async start() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MCP Server started on stdio');
  }
}

new MyMCPServer().start().catch(console.error);
```

### 5. 更多工具示例

```typescript
// 文件操作工具
export const fileTools = {
  name: 'file_operations',
  description: '读取、写入、列出文件',
  inputSchema: z.object({
    operation: z.enum(['read', 'write', 'list', 'delete']),
    path: z.string(),
    content: z.string().optional()
  }),

  async handler(args: any) {
    const fs = await import('fs/promises');
    
    switch (args.operation) {
      case 'read': {
        const content = await fs.readFile(args.path, 'utf-8');
        return { content: [{ type: 'text', text: content }] };
      }
      case 'write': {
        await fs.writeFile(args.path, args.content || '');
        return { content: [{ type: 'text', text: 'File written successfully' }] };
      }
      case 'list': {
        const files = await fs.readdir(args.path);
        return { content: [{ type: 'text', text: files.join('\n') }] };
      }
      default:
        throw new Error(`Unknown operation: ${args.operation}`);
    }
  }
};

// 数据库查询工具
export const dbTool = {
  name: 'database_query',
  description: '执行数据库查询',
  inputSchema: z.object({
    sql: z.string().describe('SQL查询语句'),
    params: z.array(z.any()).optional()
  }),

  async handler(args: any) {
    // 使用 mysql2 或 pg
    // const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    // const result = await pool.query(args.sql, args.params);
    return {
      content: [{ type: 'text', text: JSON.stringify({ rows: [], count: 0 }) }]
    };
  }
};
```

## 测试

```bash
# 编译
npm run build

# 手动测试
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | npm run dev

# MCP Inspector
npx @modelcontextprotocol/inspector npm run dev
```

## 部署

### Claude Desktop

```json
// ~/.config/claude-desktop/claude_desktop_config.json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "node",
      "args": ["/path/to/mcp-server/dist/index.js"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### Cursor / VS Code

在扩展设置中添加 MCP 服务器路径。

## 最佳实践

1. **错误处理**：始终返回有意义的错误信息
2. **类型安全**：使用 Zod 严格验证输入
3. **日志记录**：使用 `console.error` 记录关键事件
4. **性能**：长时间操作使用流式响应
5. **安全**：不记录敏感信息，定期清理日志

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
