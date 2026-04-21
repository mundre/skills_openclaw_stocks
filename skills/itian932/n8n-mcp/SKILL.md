---
name: n8n-mcp
version: "1.0.0"
description: "Operate n8n workflow automation platform via MCP (Model Context Protocol). Use when: (1) Creating, updating, or managing n8n workflows, (2) Executing or testing workflows, (3) Discovering n8n nodes and their types, (4) Managing data tables and projects, (5) Building workflows programmatically with SDK. Triggers on: 'n8n', 'workflow', 'automation', 'create workflow', 'execute workflow'."
metadata:
  openclaw:
    requires:
      env:
        - N8N_MCP_URL
        - N8N_MCP_TOKEN
      services:
        - name: n8n
          version: "2.16.1+"
          url: "http://localhost:5678"
---

# n8n MCP Integration

Connect to n8n's official MCP server to programmatically build, execute, and manage workflows.

## Version Support

- **n8n version**: 2.16.1+
- **MCP protocol**: 2024-11-05
- **Server name**: n8n MCP Server v1.1.0

## Configuration

### MCP Server Setup

In n8n UI:
1. Go to **Settings → n8n API**
2. Create an API key for REST API access
3. Create an MCP token for MCP server access

### Connection Config

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "type": "http",
      "url": "http://localhost:5678/mcp-server/http",
      "headers": {
        "Authorization": "Bearer <MCP_TOKEN>"
      }
    }
  }
}
```

### Environment Variables

```bash
export N8N_MCP_URL="http://localhost:5678/mcp-server/http"
export N8N_MCP_TOKEN="<your-mcp-token>"
```

## Available Tools

### Workflow Management

| Tool | Description |
|------|-------------|
| `search_workflows` | Search workflows with filters |
| `get_workflow_details` | Get workflow details + trigger info |
| `publish_workflow` | Activate workflow for production |
| `unpublish_workflow` | Deactivate workflow |
| `archive_workflow` | Archive a workflow |
| `update_workflow` | Update workflow from code |

### Workflow Execution

| Tool | Description |
|------|-------------|
| `execute_workflow` | Execute workflow by ID |
| `get_execution` | Get execution details |
| `test_workflow` | Test workflow with pin data |
| `prepare_test_pin_data` | Generate test data for workflow |

### Workflow Creation (SDK)

| Tool | Description |
|------|-------------|
| `get_sdk_reference` | Get SDK docs and patterns |
| `search_nodes` | Search n8n nodes by service/type |
| `get_node_types` | Get TypeScript type definitions |
| `get_suggested_nodes` | Get curated node recommendations |
| `validate_workflow` | Validate workflow code |
| `create_workflow_from_code` | Create workflow from SDK code |

### Data Tables

| Tool | Description |
|------|-------------|
| `search_data_tables` | Search data tables |
| `create_data_table` | Create new data table |
| `rename_data_table` | Rename data table |
| `add_data_table_column` | Add column to table |
| `delete_data_table_column` | Delete column |
| `rename_data_table_column` | Rename column |
| `add_data_table_rows` | Insert rows into table |

### Projects & Folders

| Tool | Description |
|------|-------------|
| `search_projects` | Search projects |
| `search_folders` | Search folders |

## Usage Patterns

### 1. Creating a Workflow

```bash
# Step 1: Get SDK reference
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_sdk_reference","arguments":{"section":"all"}}}' \
  "$N8N_MCP_URL"

# Step 2: Search nodes
curl -X POST ... -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_nodes","arguments":{"queries":["schedule trigger","slack","set"]}}}'

# Step 3: Get node types
curl -X POST ... -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_node_types","arguments":{"nodeIds":["n8n-nodes-base.scheduleTrigger","n8n-nodes-base.slack"]}}}'

# Step 4: Validate code
curl -X POST ... -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"validate_workflow","arguments":{"code":"..."}}}'

# Step 5: Create workflow
curl -X POST ... -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"create_workflow_from_code","arguments":{"code":"...","name":"My Workflow","description":"..."}}}'
```

### 2. Executing a Workflow

```bash
# Execute workflow
curl -X POST ... -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"execute_workflow","arguments":{"workflowId":"xxx"}}}'

# Get execution result
curl -X POST ... -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_execution","arguments":{"workflowId":"xxx","executionId":"yyy","includeData":true}}}'
```

### 3. Testing with Pin Data

```bash
# Prepare test data
curl -X POST ... -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"prepare_test_pin_data","arguments":{"workflowId":"xxx"}}}'

# Test workflow
curl -X POST ... -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"test_workflow","arguments":{"workflowId":"xxx","pinData":{...}}}}'
```

## SDK Workflow Example

```typescript
import { workflow, trigger, node } from 'n8n-workflow-sdk';

export default workflow({
  name: 'Daily Slack Notification',
  description: 'Send daily summary to Slack',
  nodes: [
    trigger.schedule({
      name: 'Schedule',
      rule: { interval: [{ field: 'hours', hoursInterval: 24 }] }
    }),
    node.set({
      name: 'Prepare Message',
      values: { text: 'Daily report ready!' }
    }),
    node.slack({
      name: 'Send to Slack',
      resource: 'message',
      operation: 'send',
      channel: '#general',
      text: '={{ $node["Prepare Message"].json.text }}'
    })
  ],
  connections: [
    { from: 'Schedule', to: 'Prepare Message' },
    { from: 'Prepare Message', to: 'Send to Slack' }
  ]
});
```

## MCP Protocol Notes

- **Transport**: HTTP with SSE (Server-Sent Events)
- **Content-Type**: `application/json`
- **Accept**: `application/json, text/event-stream` (required)
- **Auth**: Bearer token in Authorization header

## Common Errors

| Error | Solution |
|-------|----------|
| "Not Acceptable" | Add `Accept: application/json, text/event-stream` header |
| "Unauthorized" | Check MCP token is valid |
| "Not found" | Verify MCP server URL is correct |

## References

- **SDK Reference**: See [references/sdk-patterns.md](references/sdk-patterns.md) for detailed SDK patterns
- **Node Types**: See [references/common-nodes.md](references/common-nodes.md) for frequently used nodes
