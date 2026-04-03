import { readFile, readdir, stat } from 'fs/promises';
import { join } from 'path';

/**
 * session:start hook
 * Loads memory context into the new session so the AI has recent history.
 */
export default async function ({ context, log }) {
  const workspace = context.workspace || process.cwd();
  const memoryDir = join(workspace, 'memory');

  try {
    // Find the most recent memory file
    const files = await readdir(memoryDir)
      .then(files => files.filter(f => f.endsWith('.md')))
      .catch(() => []);

    if (files.length === 0) {
      log.debug('No memory files found to load');
      return;
    }

    // Sort by date (filename format: YYYY-MM-DD.md)
    files.sort((a, b) => b.localeCompare(a));
    const latestFile = join(memoryDir, files[0]);

    const content = await readFile(latestFile, 'utf8');

    // Inject memory as a system message at the start of the session
    if (context.sessionEntry && Array.isArray(context.sessionEntry.messages)) {
      const memoryMessage = {
        role: 'system',
        content: `[Memory context from ${files[0]}]\n\n${content}`,
        metadata: { source: 'memory-loader', timestamp: new Date().toISOString() }
      };
      context.sessionEntry.messages.unshift(memoryMessage);
      log.info(`Loaded memory from ${files[0]} (${content.length} chars)`);
    }
  } catch (error) {
    log.error('Failed to load memory:', error);
  }
}
