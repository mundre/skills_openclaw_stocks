# n8n Workflow SDK Patterns

## Core Imports

```typescript
import { workflow, trigger, node, expression } from 'n8n-workflow-sdk';
```

## Trigger Types

### Schedule Trigger

```typescript
trigger.schedule({
  name: 'Daily Trigger',
  rule: { interval: [{ field: 'hours', hoursInterval: 24 }] }
})

// Cron expression
trigger.schedule({
  name: 'Cron Trigger',
  rule: { type: 'cron', cronExpression: '0 9 * * 1-5' }  // 9am weekdays
})
```

### Webhook Trigger

```typescript
trigger.webhook({
  name: 'Webhook',
  httpMethod: 'POST',
  path: 'my-webhook',
  authentication: 'none'
})
```

### Manual Trigger

```typescript
trigger.manual({
  name: 'Manual Trigger'
})
```

## Common Nodes

### Set (Data Transformation)

```typescript
node.set({
  name: 'Transform Data',
  values: {
    message: 'Hello {{ $json.name }}',
    timestamp: '={{ $now.toISO() }}'
  },
  options: { keepOnlySetup: true }
})
```

### HTTP Request

```typescript
node.httpRequest({
  name: 'Fetch API',
  method: 'GET',
  url: 'https://api.example.com/data',
  authentication: 'predefinedCredentialType',
  nodeCredentialType: 'httpHeaderAuth'
})
```

### Code Node

```typescript
node.code({
  name: 'Custom Logic',
  language: 'javaScript',
  code: `
    const items = $input.all();
    const result = items.map(item => ({
      json: { ...item.json, processed: true }
    }));
    return result;
  `
})
```

### If Condition

```typescript
node.if({
  name: 'Check Condition',
  conditions: {
    string: [{
      value1: '={{ $json.status }}',
      operation: 'equals',
      value2: 'active'
    }]
  }
})
```

### Merge

```typescript
node.merge({
  name: 'Combine Data',
  mode: 'combine',
  combinationMode: 'mergeByPosition',
  options: {}
})
```

## Service Nodes

### Slack

```typescript
node.slack({
  name: 'Send Message',
  resource: 'message',
  operation: 'send',
  channel: '#general',
  text: '={{ $json.message }}'
})
```

### Gmail

```typescript
node.gmail({
  name: 'Send Email',
  resource: 'message',
  operation: 'send',
  to: 'user@example.com',
  subject: 'Notification',
  message: '={{ $json.body }}'
})
```

### Discord

```typescript
node.discord({
  name: 'Post to Discord',
  resource: 'message',
  operation: 'post',
  channelId: '123456789',
  content: '={{ $json.message }}'
})
```

## Expressions

### Accessing Data

```typescript
// Current node data
'={{ $json.fieldName }}'

// Previous node data
'={{ $node["Previous Node"].json.fieldName }}'

// All items
'={{ $input.all() }}'

// First item
'={{ $input.first().json }}'
```

### Built-in Functions

```typescript
// Date/Time
'={{ $now.toISO() }}'           // Current timestamp
'={{ $now.plus({days: 1}) }}'   // Tomorrow

// String
'={{ $json.name.toUpperCase() }}'
'={{ $json.text.substring(0, 100) }}'

// Array
'={{ $json.items.length }}'
'={{ $json.items.filter(i => i.active) }}'
```

## Connections

```typescript
connections: [
  // Simple: A → B
  { from: 'Node A', to: 'Node B' },

  // With output/input index
  { from: 'Node A', to: 'Node B', fromOutput: 0, toInput: 0 },

  // If node: true/false branches
  { from: 'Check', to: 'Action A', fromOutput: 0 },  // true
  { from: 'Check', to: 'Action B', fromOutput: 1 }   // false
]
```

## Error Handling

```typescript
node.set({
  name: 'Handle Error',
  values: {
    error: '={{ $json.error?.message || "Unknown error" }}'
  }
})
```

## Best Practices

1. **Always validate** before creating: `validate_workflow(code)`
2. **Get node types** before writing: `get_node_types(nodeIds)`
3. **Use expressions** for dynamic values
4. **Test with pin data** before activating
5. **Add descriptions** for complex workflows
