import { Plugin } from 'openclaw';
import type { PluginConfig } from 'openclaw';
import { Archiver } from './archiver.js';
import { Refiner } from './refiner.js';
import { mergeConfig } from './config.js';
import type { Config } from './types.js';

export default class MemoryAutoPlugin extends Plugin {
  private config: Config;
  private logger: (msg: string) => void;

  constructor() {
    super();
    this.logger = this.logger || console.log;
    // Config will be merged in onRegister when we have access to plugin config
    this.config = mergeConfig();
  }

  onRegister(pluginConfig?: PluginConfig) {
    this.logger('[MemoryAuto] Plugin registered');

    // Merge user config
    if (pluginConfig?.memoryAuto) {
      this.config = mergeConfig(pluginConfig.memoryAuto as any);
    }

    // Listen for agent startup
    this.on('agent:startup', async (agent) => {
      this.logger('[MemoryAuto] Agent startup detected');
      if (!this.config.schedule.checkOnStartup) {
        this.logger('[MemoryAuto] Startup check disabled');
        return;
      }

      try {
        const workspace = agent.workspace || process.env.OPENCLAW_WORKSPACE || process.cwd();
        const archiver = new Archiver(this.config, this.logger);
        const daily = await archiver.run(workspace);

        // If refinement enabled and we have new content, trigger refine
        if (daily && this.config.refine.enabled) {
          const refiner = new Refiner(this.config, this.logger);
          await refiner.run(workspace, daily);
        }
      } catch (err) {
        this.logger(`[MemoryAuto] Startup failed: ${err}`);
      }
    });
  }

  // Expose config for debugging
  getConfig(): Config {
    return this.config;
  }
}
