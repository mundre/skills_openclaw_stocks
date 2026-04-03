import { readFile, mkdir, writeFile } from 'fs/promises';
import { join } from 'path';

/**
 * Determines whether this conversation should be summarized.
 */
function shouldSummarize(context) {
  const msgCount = context.messages?.length || 0;
  const tokenCount = context.session?.tokenCount || 0;
  const maxTokens = context.config?.maxTokens || 128000;

  // Summarize if we have many messages or are approaching token limit
  return (
    msgCount >= 20 || // many turns
    tokenCount > maxTokens * 0.6 // 60% of limit
  );
}

/**
 * Generates a concise summary of the conversation using the agent's LLM.
 */
async function summarizeConversation(messages, log) {
  // Build conversation text for fallback summary
  const conversationText = messages
    .map(m => `${m.role === 'user' ? 'User' : m.role === 'assistant' ? 'Assistant' : m.role}: ${m.content}`)
    .join('\n');

  try {
    // Use OpenClaw's internal AI service via the global agent
    const agent = global.__OPENCLAW_AGENT__;
    if (!agent || typeof agent.generateSummary !== 'function') {
      log?.warn?.('Agent.generateSummary not available, using fallback');
      return `**Quick Summary** (${messages.length} messages):\n\n${conversationText.substring(0, 1000)}...`;
    }

    const summary = await agent.generateSummary(messages);
    return summary || `**Summary** (generated but empty)`;
  } catch (error) {
    log?.error?.('Error generating summary:', error);
    return `**Quick Summary** (${messages.length} messages):\n\n${conversationText.substring(0, 1000)}...`;
  }
}

/**
 * Writes the summary to a daily memory file in the workspace's memory directory.
 */
async function writeMemoryFile(summary, workspace) {
  const memoryDir = join(workspace, 'memory');
  await mkdir(memoryDir, { recursive: true });

  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const filePath = join(memoryDir, `${today}.md`);

  // Prepend new summary to today's file
  let existing = '';
  try {
    existing = await readFile(filePath, 'utf8');
  } catch {
    // file doesn't exist yet
  }

  const separator = existing ? '\n---\n' : '';
  const entry = `## ${new Date().toLocaleTimeString()}\n${summary}`;
  const content = entry + separator + existing;

  await writeFile(filePath, content, 'utf8');
  return filePath;
}

/**
 * Main hook entry point
 */
export default async function (context) {
  const log = context.log || console;
  const workspace = context.workspace || process.cwd();

  try {
    if (!shouldSummarize(context)) {
      log.debug('session:compact:before - skipping summarization (threshold not met)');
      return;
    }

    log.info('session:compact:before - generating summary...');
    const summary = await summarizeConversation(context.messages, log);
    const filePath = await writeMemoryFile(summary, workspace);
    log.info(`session:compact:before - summary written to ${filePath}`);
  } catch (error) {
    log.error('session:compact:before hook failed:', error);
  }
}
