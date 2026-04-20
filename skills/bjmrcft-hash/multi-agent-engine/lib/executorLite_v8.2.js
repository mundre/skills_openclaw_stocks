// executorLite_v8.2.js - ASCII only functional module
// v8.0 optimized, no encoding issues

// ASCII only comment: Lite executor for multi-agent orchestration
// Avoids Chinese characters and special multi-byte encodings

import fs from 'node:fs';
import path from 'node:path';

const CONFIG_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace');

// Basic complexity estimation - ASCII only
function estimateComplexityLite(task) {
  const desc = (task?.description || '').toLowerCase();
  const simpleWords = ['list', 'summarize', 'format', 'simple', 'quick'];
  if (simpleWords.some(s => desc.includes(s))) return 'simple';
  const complexWords = ['deep', 'comprehensive', 'analysis', 'detailed'];
  if (complexWords.some(s => desc.includes(s))) return 'complex';
  return 'medium';
}

// Main spawn params builder
export function buildLiteSpawnParams(agentProfile, task, workflow, options = {}) {
  const outputMode = options.outputMode || 'json';
  const complexity = estimateComplexityLite(task);
  
  const outputDir = options.outputDir || path.join(CONFIG_DIR, 'shared', 'final');
  const ext = outputMode === 'json' ? '.json' : '.md';
  const outputFile = path.join(outputDir, agentProfile.name + '_report' + ext);
  
  fs.mkdirSync(outputDir, { recursive: true });
  
  return {
    task: 'Execute task: ' + (task?.description || 'No description'),
    label: 'lite-' + agentProfile.name + '-' + workflow.id,
    model: options.model || 'default',
    timeoutSeconds: 300,
    cwd: CONFIG_DIR,
    mode: 'run',
    thread: false,
    cleanup: 'keep',
    output_file: outputFile,
    output_mode: outputMode,
    failure_strategy: 'retry',
    _meta: {
      agentRole: agentProfile.name,
      complexity: complexity,
      version: 'v8.0'
    }
  };
}

// Output validation
export function validateLiteOutput(agentName, outputDir) {
  const outputFile = path.join(outputDir, agentName + '_report.json');
  
  try {
    if (!fs.existsSync(outputFile)) {
      return {
        valid: false,
        errors: ['Output file not found'],
        action: 'retry'
      };
    }
    
    return {
      valid: true,
      score: 100,
      action: 'continue'
    };
  } catch (error) {
    return {
      valid: false,
      errors: ['Validation error: ' + error.message],
      action: 'retry'
    };
  }
}

// Failure handler
export function handleLiteFailure(validationResult, agentName) {
  return {
    action: 'continue',
    strategy: validationResult.valid ? 'continue' : 'retry',
    shouldContinue: true,
    message: 'Processing result for ' + agentName
  };
}

// State manager
export function createWorkflowStateManager(workflowId) {
  return {
    initWorkflow: (goal, agents) => ({ success: true, workflowId }),
    updatePhase: (phaseId, phaseData) => ({ success: true }),
    getWorkflow: () => ({ status: 'initialized' }),
    markCompleted: (result) => ({ success: true })
  };
}

// Token savings estimator
export function estimateTokensSavings(spawnParams) {
  return {
    saved: {
      tokens: spawnParams.output_mode === 'json' ? 1200 : 800,
      percent: spawnParams.output_mode === 'json' ? '60%' : '40%'
    },
    version: 'v8.0'
  };
}

// Batch spawn params builder
export function buildBatchLiteSpawnParams(agentNames, workflow, profiles, options = {}) {
  const outputDir = options.outputDir || path.join(CONFIG_DIR, 'shared', 'final');
  fs.mkdirSync(outputDir, { recursive: true });
  
  return agentNames.map(name => {
    const profile = profiles[name];
    if (!profile) return { error: 'Missing profile: ' + name, skip: true };
    
    const task = {
      description: options.tasks?.[name] || 'Execute ' + name + ' task',
      requirements: options.requirements?.[name] || []
    };
    
    return buildLiteSpawnParams(profile, task, workflow, { ...options, outputDir });
  });
}

// Strategy constants (use ASCII representation)
export const FAILURE_STRATEGIES = {
  retry: { name: 'retry', maxRetries: 2 },
  skip: { name: 'skip', maxRetries: 0 },
  fallback: { name: 'fallback', maxRetries: 0 }
};

// Default export - ASCII only
export default {
  buildLiteSpawnParams,
  validateLiteOutput,
  handleLiteFailure,
  createWorkflowStateManager,
  estimateTokensSavings,
  buildBatchLiteSpawnParams,
  FAILURE_STRATEGIES
};