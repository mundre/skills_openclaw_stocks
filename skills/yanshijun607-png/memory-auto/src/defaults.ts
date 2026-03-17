// Default configuration for memory-auto plugin
// These are sensible defaults for ANY OpenClaw user

export const DEFAULT_KEYWORDS = [
  // Chinese - common work terms
  '任务', '记得', '记住', '重要', '明天', '计划',
  '问题', '修复', '部署', '安装', '配置', '设置',
  'API', 'token', '密钥', '密码', '账号',
  'OpenClaw', '龙虾', '插件', '脚本', '命令',
  '错误', '失败', '成功', '完成', '更新',
  // English - universal terms
  'task', 'remember', 'important', 'tomorrow', 'plan',
  'issue', 'bug', 'fix', 'deploy', 'install', 'config',
  'password', 'api', 'token', 'key', 'secret',
  'script', 'command', 'run', 'exec', 'error', 'success'
];

export const DEFAULT_PATHS = {
  memoryDir: 'memory',        // daily logs
  logsDir: 'logs',
  markerSuffix: '.archived'   // marker file: .2026-03-11.archived
};

export const DEFAULT_SCHEDULE = {
  archiveHour: 9,      // 9 AM local time
  checkOnStartup: true // always check when agent starts
};

export const DEFAULT_TEMPLATES = {
  dailyLog: `# {date} Work Log

## Summary
User: {userCount}
Assistant: {assistantCount}

### Highlights
{highlights}

---
Auto-archived by openclaw-memory-auto
Refine needed: {refinePrompt}
`,
  memoryUpdate: `## [Auto] {date}
{summary}

---`
};

export const DEFAULT_REFINE = {
  enabled: false, // off by default until stable
  model: 'stepfun/step-3.5-flash:free',
  prompt: `Analyze the daily work log and extract long-term memories.

Return JSON with these keys (arrays of strings):
- skills: new abilities learned
- projects: project milestones
- preferences: user habits/preferences discovered
- data: important configs, passwords, tokens (be careful!)
- memes: inside jokes, nicknames, special terms

Be concise and factual.`
};
