// 执行引擎精简版 - v8.0 修复版
// 修复内容：
// 1. 移除重复的 aggregateWithFallbacks 函数定义
// 2. 修复 FAILURE_STRATEGY 变量引用问题
// 3. 清理语法问题

import fs from 'node:fs';
import path from 'node:path';
import { generateAgentPrompt } from './communication.js';
import { validateOutput, selectSchema, formatSchemaPrompt } from './outputSchema.js';
import { selectModel, buildModelPool } from './modelSelector.js';
import { checkModelThinking, selectThinkingLevel } from './thinkingCapabilities.js';
import { validateEnhanced, StateVersionManager, WorkflowStateManager } from './stateManager.js';
import { getFallbackTemplate, handleFailureBoundary, aggregateWithFallbacks, FAILURE_STRATEGIES } from './fallbackTemplates.js';

const CONFIG_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace');

function estimateComplexityLite(task) {
  const desc = (task?.description || '').toLowerCase();
  
  const simpleSignals = ['列出', '汇总', '格式化', '简单', '快速', 'list', 'quick'];
  if (simpleSignals.some(s => desc.includes(s))) return 'simple';
  
  const complexSignals = ['深入', '全面', '多维度', '分析', 'deep', 'comprehensive'];
  if (complexSignals.some(s => desc.includes(s))) return 'complex';
  
  return 'medium';
}

export function buildLiteSpawnParams(agentProfile, task, workflow, options = {}) {
  const outputMode = options.outputMode || 'json';
  const complexity = options.complexity || estimateComplexityLite(task);
  
  const modelResult = selectModel(agentProfile.name, {
    complexity,
    allowFree: options.allowFree !== false
  });
  
  if (modelResult.error || !modelResult.model) {
    const modelPool = buildModelPool();
    const fallbackModel = modelPool.all[0];
    if (fallbackModel) {
      modelResult.model = fallbackModel.id;
      modelResult.tier = fallbackModel.tier;
      modelResult.reason = `[降级] 复用池内首个模型: ${fallbackModel.id}`;
    }
  }
  
  const thinkingCaps = checkModelThinking(modelResult.model);
  const finalThinking = thinkingCaps.supportsThinking 
    ? selectThinkingLevel(modelResult.model, complexity) 
    : 'off';
  
  const timeoutPresets = { simple: 120, medium: 300, complex: 480 };
  const timeoutSeconds = options.timeoutSeconds || timeoutPresets[complexity] || 300;
  
  const outputDir = options.outputDir || path.join(CONFIG_DIR, 'shared', 'final');
  const ext = outputMode === 'json' ? '.json' : '.md';
  const outputFile = path.join(outputDir, `${agentProfile.name}_report${ext}`);
  
  const context = {
    goal: workflow.goal,
    output_dir: outputDir
  };
  
  const prompt = generateAgentPrompt(agentProfile, task, 'standard_task', context);
  const outputInstruction = `输出文件: ${outputFile} (${outputMode === 'json' ? 'JSON格式' : 'Markdown格式'})\n完成后输出: EXECUTION_COMPLETE`;
  const completeTask = `${prompt}\n\n${outputInstruction}`;
  
  fs.mkdirSync(outputDir, { recursive: true });
  
  return {
    task: completeTask,
    label: `lite-${agentProfile.name}-${workflow.id}`,
    model: modelResult.model,
    thinking: finalThinking !== 'off' ? finalThinking : undefined,
    timeoutSeconds,
    cwd: CONFIG_DIR,
    mode: 'run',
    thread: false,
    cleanup: 'keep',
    output_file: outputFile,
    output_mode: outputMode,
    schema: outputMode === 'json' ? selectSchema(agentProfile.name) : null,
    failure_strategy: 'retry',
    _meta: {
      agentRole: agentProfile.name,
      complexity,
      modelTier: modelResult.tier || 'unknown',
      tokensSavedEstimate: outputMode === 'json' ? '55%' : '10%',
      version: 'v8.0'
    }
  };
}

export function validateLiteOutput(agentName, outputDir, options = {}) {
  const ext = '.json';
  const outputFile = path.join(outputDir, `${agentName}_report${ext}`);
  
  try {
    if (!fs.existsSync(outputFile)) {
      return {
        valid: false,
        errors: ['输出文件不存在'],
        parsed: null,
        action: 'retry',
        strategy: 'retry',
        score: 0
      };
    }
    
    const content = fs.readFileSync(outputFile, 'utf-8');
    const enhancedValidation = validateEnhanced(content, agentName);
    
    const boundaryResult = handleFailureBoundary(
      enhancedValidation,
      { name: agentName },
      options
    );
    
    return {
      ...enhancedValidation,
      ...boundaryResult,
      outputFile
    };
  } catch (error) {
    return {
      valid: false,
      errors: [`读取失败: ${error.message}`],
      parsed: null,
      action: 'retry',
      strategy: 'retry',
      score: 0
    };
  }
}

export function handleLiteFailure(validationResult, agentName, workflow) {
  const boundaryResult = handleFailureBoundary(
    validationResult,
    { name: agentName },
    { phaseType: workflow.phaseType || 'unknown' }
  );
  
  const template = boundaryResult.template || getFallbackTemplate(agentName, 'complete');
  
  return {
    action: boundaryResult.action,
    strategy: boundaryResult.strategy,
    template: template,
    shouldContinue: boundaryResult.shouldContinue,
    message: boundaryResult.message,
    maxRetries: boundaryResult.maxRetries,
    userControlled: boundaryResult.userControlled
  };
}

export function createWorkflowStateManager(workflowId) {
  const stateFile = path.join(CONFIG_DIR, '.multi-agent-workflows.json');
  const versionManager = new StateVersionManager(stateFile);
  
  return {
    initWorkflow: (goal, agents) => {
      const state = versionManager.load();
      
      state.data[workflowId] = {
        goal: goal,
        agents: agents,
        status: 'initialized',
        phases: {},
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      return versionManager.save(state.data);
    },
    
    updatePhase: (phaseId, phaseData) => {
      const state = versionManager.load();
      
      if (!state.data[workflowId]) {
        return { success: false, error: '工作流不存在' };
      }
      
      state.data[workflowId].phases[phaseId] = {
        ...phaseData,
        updatedAt: new Date().toISOString()
      };
      state.data[workflowId].updatedAt = new Date().toISOString();
      
      return versionManager.save(state.data);
    },
    
    getWorkflow: () => {
      const state = versionManager.load();
      return state.data[workflowId] || null;
    },
    
    markCompleted: (result) => {
      const state = versionManager.load();
      
      if (!state.data[workflowId]) {
        return { success: false, error: '工作流不存在' };
      }
      
      state.data[workflowId].status = 'completed';
      state.data[workflowId].result = result;
      state.data[workflowId].completedAt = new Date().toISOString();
      
      return versionManager.save(state.data);
    }
  };
}

export function estimateTokensSavings(spawnParams) {
  const baselineTokens = {
    promptOld: 800,
    contextOld: 500,
    totalOld: 1300
  };
  
  const optimizedTokens = {
    promptNew: spawnParams.output_mode === 'json' ? 80 : 400,
    contextNew: spawnParams.output_mode === 'json' ? 20 : 100,
    totalNew: spawnParams.output_mode === 'json' ? 100 : 500
  };
  
  const savedTokens = baselineTokens.totalOld - optimizedTokens.totalNew;
  const savedPercent = Math.round((savedTokens / baselineTokens.totalOld) * 100);
  
  return {
    baseline: baselineTokens,
    optimized: optimizedTokens,
    saved: {
      tokens: savedTokens,
      percent: savedPercent + '%'
    },
    mode: spawnParams.output_mode,
    version: spawnParams._meta?.version || 'v8.0'
  };
}

export function buildBatchLiteSpawnParams(agentNames, workflow, profiles, options = {}) {
  const outputDir = options.outputDir || path.join(CONFIG_DIR, 'shared', 'final');
  fs.mkdirSync(outputDir, { recursive: true });
  
  return agentNames.map(agentName => {
    const profile = profiles[agentName];
    if (!profile) {
      return {
        error: `代理配置缺失: ${agentName}`,
        agentName,
        skip: true
      };
    }
    
    const task = {
      description: options.tasks?.[agentName] || `执行 ${agentName} 的研究任务`,
      requirements: options.requirements?.[agentName] || []
    };
    
    return buildLiteSpawnParams(profile, task, workflow, {
      ...options,
      outputDir
    });
  });
}

export default {
  buildLiteSpawnParams,
  validateLiteOutput,
  handleLiteFailure,
  aggregateWithFallbacks,
  createWorkflowStateManager,
  estimateTokensSavings,
  buildBatchLiteSpawnParams,
  FAILURE_STRATEGIES
};