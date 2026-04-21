# Common n8n Nodes Reference

Quick reference for frequently used n8n nodes with their IDs and discriminators.

## Trigger Nodes

| Node | ID | Description |
|------|------|------|
| Schedule Trigger | `n8n-nodes-base.scheduleTrigger` | Time-based triggers |
| Webhook | `n8n-nodes-base.webhook` | HTTP webhook endpoint |
| Manual Trigger | `n8n-nodes-base.manualTrigger` | Manual execution |
| Form Trigger | `n8n-nodes-base.formTrigger` | Form submission |

## Logic Nodes

| Node | ID | Description |
|------|------|------|
| If | `n8n-nodes-base.if` | Conditional branching |
| Switch | `n8n-nodes-base.switch` | Multiple conditions |
| Merge | `n8n-nodes-base.merge` | Combine data streams |
| Split In Batches | `n8n-nodes-base.splitInBatches` | Batch processing |
| Loop Over Items | `n8n-nodes-base.split` | Iterate over items |

## Transform Nodes

| Node | ID | Description |
|------|------|------|
| Set | `n8n-nodes-base.set` | Set/transform values |
| Code | `n8n-nodes-base.code` | Custom JavaScript/Python |
| Edit Fields | `n8n-nodes-base.editFields` | Rename/remove fields |
| Filter | `n8n-nodes-base.filter` | Filter items |
| Sort | `n8n-nodes-base.sort` | Sort items |
| Remove Duplicates | `n8n-nodes-base.removeDuplicates` | Deduplicate |

## HTTP & API

| Node | ID | Description |
|------|------|------|
| HTTP Request | `n8n-nodes-base.httpRequest` | Generic HTTP calls |
| HTTP Request (Legacy) | `n8n-nodes-base.httpRequest` | Older version |

## Communication

| Node | ID | Resource | Operations |
|------|------|----------|------------|
| Slack | `n8n-nodes-base.slack` | message | send, post |
| Discord | `n8n-nodes-base.discord` | message | post |
| Telegram | `n8n-nodes-base.telegram` | message | send |
| Gmail | `n8n-nodes-base.gmail` | message | send |
| Email (SMTP) | `n8n-nodes-base.emailSend` | - | send |

## Database

| Node | ID | Description |
|------|------|------|
| Postgres | `n8n-nodes-base.postgres` | PostgreSQL operations |
| MySQL | `n8n-nodes-base.mySql` | MySQL operations |
| MongoDB | `n8n-nodes-base.mongoDb` | MongoDB operations |
| Redis | `n8n-nodes-base.redis` | Redis operations |

## File Operations

| Node | ID | Description |
|------|------|------|
| Read Binary File | `n8n-nodes-base.readBinaryFile` | Read files |
| Write Binary File | `n8n-nodes-base.writeBinaryFile` | Write files |
| Spreadsheet File | `n8n-nodes-base.spreadsheetFile` | Excel/CSV |
| JSON | `n8n-nodes-base.convertToFile` | JSON conversion |

## AI & LLM

| Node | ID | Description |
|------|------|------|
| OpenAI | `n8n-nodes-base.openAi` | GPT models |
| Anthropic | `@n8n/n8n-nodes-langchain.anthropic` | Claude models |
| LangChain | `@n8n/n8n-nodes-langchain` | LangChain tools |
| AI Agent | `@n8n/n8n-nodes-langchain.lmChatOpenAi` | AI agent |

## Date & Time

| Node | ID | Description |
|------|------|------|
| Date & Time | `n8n-nodes-base.dateTime` | Date operations |
| Cron | `n8n-nodes-base.cron` | Cron scheduling |
| Wait | `n8n-nodes-base.wait` | Delay execution |

## Search Query Examples

```bash
# Search for specific services
search_nodes(["slack", "gmail", "telegram"])

# Search for triggers
search_nodes(["schedule trigger", "webhook", "form"])

# Search for logic nodes
search_nodes(["if", "switch", "merge", "code", "set"])

# Search for AI nodes
search_nodes(["openai", "anthropic", "langchain"])
```

## Node Type with Discriminators

When calling `get_node_types`, include discriminators from search results:

```json
[
  "n8n-nodes-base.slack",
  {
    "nodeId": "n8n-nodes-base.slack",
    "resource": "message",
    "operation": "send"
  }
]
```
