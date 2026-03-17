import { PluginConfig } from 'openclaw';
import {
  MemoryAutoConfig,
  DEFAULT_KEYWORDS,
  DEFAULT_PATHS,
  DEFAULT_SCHEDULE,
  DEFAULT_TEMPLATES,
  DEFAULT_REFINE
} from './defaults.js';
import type { Config } from './types.js';

export function mergeConfig(userConfig?: MemoryAutoConfig): Config {
  return {
    keywords: userConfig?.keywords ?? DEFAULT_KEYWORDS,
    paths: {
      ...DEFAULT_PATHS,
      ...userConfig?.paths
    },
    schedule: {
      ...DEFAULT_SCHEDULE,
      ...userConfig?.schedule
    },
    templates: {
      ...DEFAULT_TEMPLATES,
      ...userConfig?.templates
    },
    refine: {
      ...DEFAULT_REFINE,
      ...userConfig?.refine
    }
  };
}

// Helper: get workspace path from OpenClaw context
export function getWorkspacePath(plugin: PluginConfig): string {
  // OpenClaw provides workspace in config or env
  return plugin.workspace || process.env.OPENCLAW_WORKSPACE || process.cwd();
}
