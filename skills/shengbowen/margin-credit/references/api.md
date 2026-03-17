# hiAgentChat API Reference (智享两融 / margin-credit)

## Endpoint

```
POST https://aigctest.gf.com.cn/api/aigc/api/base/hiAgentChat?robotId=cjzj&agentId=mfis2agent
```

## Request

- **Headers**: `Content-Type: application/json`, `accept: text/event-stream`, `Cookie: <GF_AGENT_COOKIE>`
- **Body** (only API-related fields; do not inject user/session metadata):

```json
{
  "question": "<用户问题>",
  "conversationId": "",
  "mindSet": "auto",
  "agentId": "mfis2agent",
  "robotId": "cjzj",
  "currentRobotId": "cjzj",
  "extendParams": { "webSearchMode": "auto" }
}
```

- **conversationId**: Empty for new conversation; can be set for multi-turn if the API returns and requires it.

## Authentication

- **GF_AGENT_COOKIE**: Full Cookie string (same as investment-analysis). Set via environment; do not hardcode or commit.

## Response format and parsing

- **Content type**: SSE (`text/event-stream`).
- **Events**: Each event line is `data: <JSON>` (no space after `data:`).
- **Fields to extract**: From each parsed `data` object, take **`answer`** only as the reply content. Multiple events may be sent (streaming); the script concatenates all `answer` values in order and outputs once.
- **stdout**: Script outputs only the concatenated content from `answer`; no other fields (sources, conversationId, extendData, etc.) are appended.
- **Errors**: If the payload has `code` (non-zero) and `message`, the script logs the message to stderr and exits with non-zero code.

### Sample data line (structure)

One SSE line (IDs shortened for readability):

```
data:{"event":null,"answer":"根据","messageId":"msg-7bf1bd68-592b-41d0-9283-886a73a6c37b","conversationId":"conv-cdd562d7-01e8-4b9c-8508-dd3f4611db1c","moduleType":null,"agentId":"mfis2agent","realQuestion":null,"sources":null,"extendData":null,"relateQuestions":null,"relativeAgents":null,"suffixCard":null}
```

- **Parse**: `answer` → `"根据"` (this segment). Multiple chunks are concatenated in order.
- Other fields (`extendData`, `realQuestion`, `conversationId`, etc.) are not used for stdout. For this agent, `extendData` is often null.

## Security

Do not commit `GF_AGENT_COOKIE` or any token to the repository. Use environment variables or a secure secret store.
