# ThinkForce Skill

Dispatch tasks to your ThinkForce AI agent team at [app.thinkforce.ai](https://app.thinkforce.ai) and poll for results — all via the REST API. No server setup needed.

---

## Getting Your API Key

1. Go to **[app.thinkforce.ai](https://app.thinkforce.ai)** and sign up / log in.
2. Open **Settings** → **ThinkForce API**.
3. Click **+ Generate API Key** — copy and save it.

Use your key as the `X-TF-API-Key` header on every request.

---

## Quick Start

### Step 1 — Get Your Company ID

Your API key automatically identifies your company:

```
GET https://app.thinkforce.ai/api/companies
X-TF-API-Key: tf_your_key_here
```

**Response:**
```json
{
  "companyId": "your-company-id",
  "name": "Acme Corp",
  "status": "active",
  "agentCount": 4
}
```

### Step 2 — List Your Agents

```
POST https://app.thinkforce.ai/api/agents
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{ "action": "list", "companyId": "your-company-id" }
```

**Response:**
```json
[
  { "id": "abc123", "agentName": "Acme CEO", "agentRole": "CEO" },
  { "id": "def456", "agentName": "Dev", "agentRole": "Developer" }
]
```

### Step 3 — Dispatch a Task

```
POST https://app.thinkforce.ai/api/agent-task
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "companyID": "your-company-id",
  "targetAgentId": "abc123",
  "task": "Research the top 5 competitor apps and summarize their pricing."
}
```

**Response:**
```json
{
  "taskId": "task-1773947855985-abc12",
  "status": "running"
}
```

### Step 4 — Poll for Result

```
GET https://app.thinkforce.ai/api/agent-task?taskId=<taskId>&companyId=<companyId>
X-TF-API-Key: tf_your_key_here
```

Poll every 5–8 seconds. Most tasks complete in 15–90 seconds.

**Completed response:**
```json
{
  "taskId": "task-1773947855985-abc12",
  "status": "complete",
  "result": "Here are the top 5 competitors..."
}
```

---

## Full JavaScript Example

```javascript
const API_KEY = 'tf_your_key_here';
const BASE = 'https://app.thinkforce.ai/api';

// 1. Get company
const co = await fetch(`${BASE}/companies`, {
  headers: { 'X-TF-API-Key': API_KEY }
}).then(r => r.json());

const companyID = co.companyId;

// 2. List agents to find the CEO
const agents = await fetch(`${BASE}/agents`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'X-TF-API-Key': API_KEY },
  body: JSON.stringify({ action: 'list', companyId: companyID }),
}).then(r => r.json());

const ceo = agents.find(a => a.agentRole === 'CEO');

// 3. Dispatch task
const { taskId } = await fetch(`${BASE}/agent-task`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'X-TF-API-Key': API_KEY },
  body: JSON.stringify({
    companyID,
    targetAgentId: ceo.id,
    task: 'Write a 30-day growth plan.',
  }),
}).then(r => r.json());

// 4. Poll for result
let result;
while (!result) {
  await new Promise(r => setTimeout(r, 6000));
  const data = await fetch(
    `${BASE}/agent-task?taskId=${taskId}&companyId=${companyID}`,
    { headers: { 'X-TF-API-Key': API_KEY } }
  ).then(r => r.json());

  if (data.result) result = data.result;
  if (data.status === 'error') throw new Error(data.error);
}

console.log(result);
```

---

## Missions API

Missions are multi-step orchestrated workflows — create a mission, break it into subtasks, assign agents, and auto-execute the whole thing.

### Create a Mission

```
POST https://app.thinkforce.ai/api/missions
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "companyId": "your-company-id",
  "title": "Launch Q2 Growth Campaign",
  "description": "Research competitors, draft content plan, and build outreach strategy",
  "priority": "high",
  "createdBy": "user-id-optional"
}
```

**Response:**
```json
{
  "id": "mission-abc123",
  "status": "planning",
  "title": "Launch Q2 Growth Campaign",
  ...
}
```

### Get a Mission (with subtasks)

```
GET https://app.thinkforce.ai/api/missions/{missionId}?companyId=your-company-id
X-TF-API-Key: tf_your_key_here
```

Returns `{ mission, subtasks }`.

### List All Missions

```
GET https://app.thinkforce.ai/api/missions?companyId=your-company-id
X-TF-API-Key: tf_your_key_here
```

### Update a Mission

```
PATCH https://app.thinkforce.ai/api/missions/{missionId}
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "companyId": "your-company-id",
  "status": "active"
}
```

Status values: `planning` → `active` → `completed` | `cancelled`. Completing (`status: "completed"`) triggers a mission completion email + Slack notification automatically.

### Auto-Decompose into Subtasks

Let AI break the mission into 5–9 actionable subtasks automatically:

```
POST https://app.thinkforce.ai/api/missions/{missionId}/decompose
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "title": "Launch Q2 Growth Campaign",
  "description": "Research competitors, draft content plan, and build outreach strategy"
}
```

**Response:**
```json
{
  "subtasks": [
    { "title": "Research top 5 competitors", "workstationKey": "researching" },
    { "title": "Draft content calendar", "workstationKey": "working" },
    ...
  ]
}
```

### Add a Subtask

```
POST https://app.thinkforce.ai/api/missions/{missionId}/subtasks
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "companyId": "your-company-id",
  "title": "Research target audience",
  "workstationKey": "researching",
  "assignedAgentId": "agent-id-optional",
  "runInstructions": "Focus on 18-35 demographic in US markets"
}
```

`workstationKey` options: `working` | `researching` | `syncing` | `error`

### Update / Delete a Subtask

```
PATCH https://app.thinkforce.ai/api/missions/{missionId}/subtasks/{subtaskId}
Content-Type: application/json

{
  "companyId": "your-company-id",
  "status": "done",
  "output": "Research complete. Key finding: ..."
}
```

For delete: `DELETE` same URL with `companyId` in body/query, or `POST` with `{ "action": "delete" }`.

### Run a Subtask (execute with assigned agent)

```
POST https://app.thinkforce.ai/api/missions/{missionId}/subtasks/{subtaskId}/run
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "companyId": "your-company-id",
  "initiatedByUserId": "user-id-optional"
}
```

The subtask runs via the assigned agent's `agent-task` pipeline. Check mission status after to see output.

### Auto-Execute the Entire Mission

Runs all subtasks sequentially with assigned agents:

```
POST https://app.thinkforce.ai/api/missions/{missionId}/auto-execute
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "companyId": "your-company-id"
}
```

### Publish Mission Report (PDF)

After a mission reaches `completed`, generate and publish a PDF report:

```
POST https://app.thinkforce.ai/api/publish-mission
X-TF-API-Key: tf_your_key_here
Content-Type: application/json

{
  "companyId": "your-company-id",
  "missionId": "mission-abc123",
  "userId": "user-id-optional"
}
```

Returns `{ publishedPdfUrl: "https://storage.googleapis.com/..." }`.

---

### Full Mission Workflow (JS Example)

```javascript
const BASE = 'https://app.thinkforce.ai/api';
const HEADERS = { 'Content-Type': 'application/json', 'X-TF-API-Key': 'tf_your_key_here' };
const companyId = 'your-company-id';

// 1. Create mission
const { id: missionId } = await fetch(`${BASE}/missions`, {
  method: 'POST', headers: HEADERS,
  body: JSON.stringify({ companyId, title: 'Q2 Campaign', description: 'Research + content plan', priority: 'high' })
}).then(r => r.json());

// 2. Auto-decompose into subtasks
const { subtasks } = await fetch(`${BASE}/missions/${missionId}/decompose`, {
  method: 'POST', headers: HEADERS,
  body: JSON.stringify({ title: 'Q2 Campaign', description: 'Research + content plan' })
}).then(r => r.json());

// 3. Add each subtask (assign agents as needed)
for (const st of subtasks) {
  await fetch(`${BASE}/missions/${missionId}/subtasks`, {
    method: 'POST', headers: HEADERS,
    body: JSON.stringify({ companyId, ...st, assignedAgentId: 'agent-id' })
  });
}

// 4. Auto-execute all subtasks
await fetch(`${BASE}/missions/${missionId}/auto-execute`, {
  method: 'POST', headers: HEADERS,
  body: JSON.stringify({ companyId })
});

// 5. Mark complete + publish PDF
await fetch(`${BASE}/missions/${missionId}`, {
  method: 'PATCH', headers: HEADERS,
  body: JSON.stringify({ companyId, status: 'completed' })
});
const { publishedPdfUrl } = await fetch(`${BASE}/publish-mission`, {
  method: 'POST', headers: HEADERS,
  body: JSON.stringify({ companyId, missionId })
}).then(r => r.json());
```

---

## Notes

- **CEO agent is always created first** during onboarding and orchestrates your team automatically.
- **Model routing**: If your account is linked to OpenAI Codex (ChatGPT Pro OAuth), tasks route through `gpt-5.4` automatically.
- **Tools available**: Google Search, Website Fetch, Memory Manager, Web Browser, and more — enabled per agent.
- **API key is per-company**: One key covers all agents. Rotate anytime from Settings.
