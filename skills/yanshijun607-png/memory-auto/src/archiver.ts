import { promises as fs } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import type { Config, DailyLog, Highlight, TranscriptMessage } from './types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = new URL('.', import.meta.url).pathname;

export class Archiver {
  private config: Config;
  private logger: (msg: string) => void;

  constructor(config: Config, logger: (msg: string) => void = console.log) {
    this.config = config;
    this.logger = logger;
  }

  async run(workspace: string): Promise<DailyLog | null> {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yStr = yesterday.toISOString().split('T')[0];
    const dailyFile = join(workspace, this.config.paths.memoryDir, `${yStr}.md`);

    this.logger(`[Archiver] Check: ${yStr}`);

    // Check if already archived
    try {
      await fs.access(dailyFile);
      this.logger('[Archiver] Already exists, skip');
      return null;
    } catch {
      // continue
    }

    // Find all transcript files
    const transcripts = await this.findTranscripts(workspace);
    if (transcripts.length === 0) {
      this.logger('[Archiver] ERROR: No transcripts found');
      throw new Error('No transcript files found');
    }

    this.logger(`[Archiver] Scanning ${transcripts.length} transcript(s)`);

    // Extract messages from yesterday
    const { messages, skipped } = await this.extractMessages(transcripts, yesterday);
    this.logger(`[Archiver] Found ${messages.length} messages (skipped ${skipped} lines)`);

    if (messages.length === 0) {
      this.logger('[Archiver] No messages for yesterday, creating empty marker');
      await fs.mkdir(join(workspace, this.config.paths.memoryDir), { recursive: true });
      await fs.writeFile(dailyFile, '', 'utf8');
      await this.createMarker(workspace, yStr);
      return null;
    }

    // Build highlights
    const highlights = this.extractHighlights(messages);
    this.logger(`[Archiver] Extracted ${highlights.length} highlights`);

    // Build daily log
    const userCount = messages.filter(m => m.role === 'user').length;
    const asstCount = messages.filter(m => m.role === 'assistant').length;

    const dailyLog: DailyLog = {
      date: yStr,
      userCount,
      assistantCount: asstCount,
      highlights,
      rawMessages: messages.length,
      skippedLines: skipped
    };

    // Render and write
    const content = this.renderDailyLog(dailyLog);
    await fs.mkdir(join(workspace, this.config.paths.memoryDir), { recursive: true });
    await fs.writeFile(dailyFile, content, 'utf8');
    this.logger(`[Archiver] Wrote: ${dailyFile}`);

    // Create marker
    await this.createMarker(workspace, yStr);

    return dailyLog;
  }

  private async findTranscripts(workspace: string): Promise<string[]> {
    const agentsDir = join(workspace, 'agents');
    const sessionsGlob = join(agentsDir, '*', 'sessions', '*.jsonl');
    // For now, we'll use a simple glob pattern
    // In production, use fast-glob or similar
    import('fast-glob').then(fg => {
      // ...
    });
    // Fallback: hard-coded path for now (will be improved)
    const defaultPath = join(workspace, 'agents', 'main', 'sessions');
    try {
      const files = await fs.readdir(defaultPath);
      return files
        .filter(f => f.endsWith('.jsonl'))
        .map(f => join(defaultPath, f));
    } catch {
      return [];
    }
  }

  private async extractMessages(
    files: string[],
    targetDate: Date
  ): Promise<{ messages: Array<{ role: 'user' | 'assistant'; text: string; time: Date }>; skipped: number }> {
    const startOfDay = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate());
    const endOfDay = new Date(startOfDay);
    endOfDay.setDate(endOfDay.getDate() + 1);

    const messages: Array<{ role: 'user' | 'assistant'; text: string; time: Date }> = [];
    let skipped = 0;

    for (const file of files) {
      try {
        const content = await fs.readFile(file, 'utf8');
        const lines = content.split('\n').filter(l => l.trim());
        for (const line of lines) {
          try {
            const msg = JSON.parse(line) as TranscriptMessage;
            if (msg.type !== 'message' || !msg.message) continue;

            // Parse UTC timestamp and convert to local
            const utc = new Date(msg.timestamp);
            const local = new Date(utc.getTime() + (utc.getTimezoneOffset() * 60000));

            if (local >= startOfDay && local < endOfDay) {
              const textObj = msg.message.content.find(c => c.type === 'text');
              if (textObj?.text) {
                messages.push({
                  role: msg.message.role,
                  text: textObj.text,
                  time: local
                });
              }
            }
          } catch {
            skipped++;
          }
        }
      } catch {
        // Skip unreadable files
      }
    }

    return { messages, skipped };
  }

  private extractHighlights(messages: Array<{ role: 'user' | 'assistant'; text: string }>): Highlight[] {
    const highlights: Highlight[] = [];
    const keywords = this.config.keywords;

    for (const msg of messages) {
      for (const kw of keywords) {
        if (msg.text.toLowerCase().includes(kw.toLowerCase())) {
          const snippet = msg.text.substring(0, Math.min(80, msg.text.length)) + (msg.text.length > 80 ? '...' : '');
          highlights.push({
            role: msg.role,
            snippet
          });
          break; // only first keyword per message
        }
      }
    }

    return highlights;
  }

  private renderDailyLog(daily: DailyLog): string {
    const highlightsText = daily.highlights.length > 0
      ? daily.highlights.map(h => `- ${h.role === 'user' ? 'User' : 'Asst'}: ${h.snippet}`).join('\n')
      : 'No highlights';

    const template = this.config.templates.dailyLog;

    return template
      .replace(/{date}/g, daily.date)
      .replace(/{userCount}/g, String(daily.userCount))
      .replace(/{assistantCount}/g, String(daily.assistantCount))
      .replace(/{highlights}/g, highlightsText)
      .replace(/{refinePrompt}/g, daily.highlights.length > 0 ? 'See logs/last_refine_prompt.txt' : 'none');
  }

  private async createMarker(workspace: string, dateStr: string): Promise<void> {
    const marker = join(workspace, this.config.paths.memoryDir, `.${dateStr}${this.config.paths.markerSuffix}`);
    await fs.writeFile(marker, 'archived', 'utf8');
  }
}
