import { promises as fs } from 'fs';
import { join } from 'path';
import type { Config, RefineResult } from './types.js';

export class Refiner {
  private config: Config;
  private logger: (msg: string) => void;

  constructor(config: Config, logger: (msg: string) => void = console.log) {
    this.config = config;
    this.logger = logger;
  }

  async run(workspace: string, dailyLog?: any): Promise<RefineResult | null> {
    if (!this.config.refine.enabled) {
      this.logger('[Refiner] Disabled by config');
      return null;
    }

    const promptFile = join(workspace, this.config.paths.logsDir, 'last_refine_prompt.txt');
    try {
      await fs.access(promptFile);
    } catch {
      this.logger('[Refiner] No prompt file, skipping');
      return null;
    }

    this.logger('[Refiner] Starting refinement...');

    try {
      const prompt = await fs.readFile(promptFile, 'utf8');
      const result = await this.callAI(prompt);
      await this.updateMemory(workspace, result);
      await fs.unlink(promptFile); // clear prompt after success
      this.logger('[Refiner] Completed');
      return result;
    } catch (err) {
      this.logger(`[Refiner] ERROR: ${err}`);
      return null;
    }
  }

  private async callAI(prompt: string): Promise<RefineResult> {
    // TODO: integrate with OpenClaw's AI runtime or direct API
    // For now, return empty (manual refinement)
    this.logger('[Refiner] AI call not implemented yet');
    return {};
  }

  private async updateMemory(workspace: string, result: RefineResult): Promise<void> {
    const memFile = join(workspace, 'MEMORY.md');
    const dateStr = new Date().toISOString().split('T')[0];

    let content = '';
    if (Object.keys(result).length > 0) {
      content = `\n## [Auto] ${dateStr}\n`;
      for (const [key, values] of Object.entries(result) as [keyof RefineResult, string[]][]) {
        if (values?.length) {
          content += `\n### ${key}\n`;
          content += values.map(v => `- ${v}`).join('\n');
        }
      }
      content += '\n---\n';
    }

    await fs.appendFile(memFile, content, 'utf8');
  }
}
