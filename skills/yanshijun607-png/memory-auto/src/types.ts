// Types for the memory-auto plugin

export interface MemoryAutoConfig {
  keywords?: string[];
  paths?: {
    memoryDir?: string;
    logsDir?: string;
    markerSuffix?: string;
  };
  schedule?: {
    archiveHour?: number;
    checkOnStartup?: boolean;
  };
  templates?: {
    dailyLog?: string;
    memoryUpdate?: string;
  };
  refine?: {
    enabled?: boolean;
    model?: string;
    prompt?: string;
  };
}

export interface Highlight {
  role: 'user' | 'assistant';
  snippet: string;
}

export interface DailyLog {
  date: string; // YYYY-MM-DD
  userCount: number;
  assistantCount: number;
  highlights: Highlight[];
  rawMessages: number;
  skippedLines: number;
}

export interface RefineResult {
  skills?: string[];
  projects?: string[];
  preferences?: string[];
  data?: string[];
  memes?: string[];
}

// Transcript message structure (OpenClaw session format)
export interface TranscriptMessage {
  type: 'message' | 'session' | 'model_change' | string;
  id: string;
  parentId?: string;
  timestamp: string; // ISO 8601 UTC
  message?: {
    role: 'user' | 'assistant';
    content: Array<{ type: 'text' | 'image' | string; text?: string }>;
  };
}
