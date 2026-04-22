/**
 * Arshis-Game-Design-Pro - OpenClaw Plugin
 * 商业级游戏策划专业工具
 * 
 * 使用 OpenClaw 默认模型，无需单独配置 API Key
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 脚本路径
const SCRIPTS_DIR = path.join(__dirname, 'scripts');
const GENERATOR = path.join(SCRIPTS_DIR, 'generator.py');
const REVIEWER = path.join(SCRIPTS_DIR, 'reviewer.py');
const WORLDVIEW = path.join(SCRIPTS_DIR, 'worldview_manager.py');
const VERSION_MANAGER = path.join(SCRIPTS_DIR, 'version_manager.py');
const TEMPLATES = path.join(SCRIPTS_DIR, 'templates.py');
const CONSISTENCY_CHECKER = path.join(SCRIPTS_DIR, 'consistency_checker.py');
const DATA_ANALYZER = path.join(SCRIPTS_DIR, 'data_analyzer.py');
const TEMPLATES_MOBAS = path.join(SCRIPTS_DIR, 'templates_mobas.py');

/**
 * 使用 OpenClaw LLM 生成内容
 * 优势：
 * - 无需单独配置 API Key
 * - 自动使用 OpenClaw 默认模型（如 dashscope/qwen3.5-plus）
 * - 支持模型切换
 * - 统一用量统计
 */
async function callOpenClawLLM(prompt, context) {
  try {
    // 调用 OpenClaw 的 LLM 工具
    // 在实际插件中，使用 context.callTool('llm', { prompt })
    
    // 当前通过 Python 脚本处理
    const result = await runPythonScript(GENERATOR, ['--llm-prompt', prompt]);
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * 执行 Python 脚本
 */
function runPythonScript(script, args = []) {
  return new Promise((resolve, reject) => {
    const process = spawn('python3', [script, ...args]);
    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(stdout));
        } catch (e) {
          resolve({ output: stdout });
        }
      } else {
        reject(new Error(`Script failed: ${stderr}`));
      }
    });
  });
}

/**
 * Tool: generate_design
 * 生成策划案 - 使用 OpenClaw 默认模型
 */
export async function generate_design(args, context) {
  try {
    const { doc_type, topic, details = '', word_count = 5000 } = args;
    
    if (!doc_type || !topic) {
      return { error: 'doc_type and topic are required' };
    }
    
    // 构建提示词
    const prompt = buildDesignPrompt(doc_type, topic, details, word_count);
    
    // 使用 OpenClaw 默认模型生成
    const result = await callOpenClawLLM(prompt, context);
    
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * 构建策划案生成提示词
 */
function buildDesignPrompt(doc_type, topic, details, word_count) {
  const templates = {
    'worldview': '世界观策划案',
    'system': '系统策划案',
    'numeric': '数值策划案',
    'level': '关卡策划案',
    'story': '剧情策划案'
  };
  
  return `你是一位资深游戏策划总监，有 10 年商业游戏项目经验。

请撰写一份完整的《${templates[doc_type] || '游戏策划案'}》，主题：${topic}

要求：
1. 专业性：使用商业项目标准格式
2. 完整性：覆盖所有必要章节
3. 详细度：总字数${word_count}字以上
4. 实用性：包含配置表、公式、流程图

额外信息：${details || '无特殊要求'}

请使用 Markdown 格式输出。`;
}

/**
 * Tool: modify_design_section
 * 修改策划案的特定章节（带版本管理）
 */
export async function modify_design_section(args, context) {
  try {
    const { version, section, content, change_log = '' } = args;
    
    if (!section || !content) {
      return { error: 'section and content are required' };
    }
    
    // 临时保存新章节内容到文件
    const fs = await import('fs');
    const tempFile = path.join(SCRIPTS_DIR, 'temp_section.md');
    fs.writeFileSync(tempFile, content, 'utf-8');
    
    // 调用版本管理器
    const result = await runPythonScript(VERSION_MANAGER, [
      'modify', version || 'v1.0', section, tempFile
    ]);
    
    // 清理临时文件
    fs.unlinkSync(tempFile);
    
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: save_version
 * 保存策划案版本
 */
export async function save_version(args, context) {
  try {
    const { content, version, change_log = '', project = 'default' } = args;
    
    if (!content || !version) {
      return { error: 'content and version are required' };
    }
    
    // 临时保存内容到文件
    const fs = await import('fs');
    const tempFile = path.join(SCRIPTS_DIR, 'temp_design.md');
    fs.writeFileSync(tempFile, content, 'utf-8');
    
    // 调用版本管理器
    const result = await runPythonScript(VERSION_MANAGER, [
      'save', version, tempFile
    ]);
    
    // 清理临时文件
    fs.unlinkSync(tempFile);
    
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: compare_versions
 * 对比两个版本的差异
 */
export async function compare_versions(args, context) {
  try {
    const { version1, version2, project = 'default' } = args;
    
    if (!version1 || !version2) {
      return { error: 'version1 and version2 are required' };
    }
    
    const result = await runPythonScript(VERSION_MANAGER, [
      'compare', version1, version2
    ]);
    
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: list_versions
 * 列出所有版本
 */
export async function list_versions(args, context) {
  try {
    const result = await runPythonScript(VERSION_MANAGER, ['list']);
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: get_template
 * 获取策划案模板
 */
export async function get_template(args, context) {
  try {
    const { template_type } = args;
    
    if (!template_type) {
      return { error: 'template_type is required' };
    }
    
    const result = await runPythonScript(TEMPLATES, ['get', template_type]);
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: list_templates
 * 列出所有可用模板
 */
export async function list_templates(args, context) {
  try {
    const result = await runPythonScript(TEMPLATES, ['list']);
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: generate_from_template
 * 从模板生成策划案
 */
export async function generate_from_template(args, context) {
  try {
    const { template_type, fill_data = {} } = args;
    
    if (!template_type) {
      return { error: 'template_type is required' };
    }
    
    // 构建命令参数
    const cmdArgs = ['generate', template_type];
    if (Object.keys(fill_data).length > 0) {
      cmdArgs.push(JSON.stringify(fill_data));
    }
    
    const result = await runPythonScript(TEMPLATES, cmdArgs);
    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: check_consistency
 * 检查新内容的一致性（角色/活动/系统）
 */
export async function check_consistency(args, context) {
  try {
    const { content_type, content_data } = args;
    
    if (!content_type || !content_data) {
      return { error: 'content_type and content_data are required' };
    }
    
    // 临时保存内容到文件
    const fs = await import('fs');
    const tempFile = path.join(SCRIPTS_DIR, 'temp_check.json');
    fs.writeFileSync(tempFile, JSON.stringify(content_data, null, 2), 'utf-8');
    
    // 调用一致性检查器
    const checkType = `check-${content_type}`;
    const result = await runPythonScript(CONSISTENCY_CHECKER, [checkType, tempFile]);
    
    // 清理临时文件
    fs.unlinkSync(tempFile);
    
    return result;
  } catch (error) {
    return { error: error.message };
  }
}
export async function review_design(args) {
  try {
    const { content, doc_type = 'system' } = args;
    
    if (!content) {
      return { error: 'content is required' };
    }

    // 临时保存内容到文件
    const fs = await import('fs');
    const tempFile = path.join(SCRIPTS_DIR, 'temp_design.md');
    fs.writeFileSync(tempFile, content, 'utf-8');

    const result = await runPythonScript(REVIEWER, [tempFile, doc_type]);
    
    // 清理临时文件
    fs.unlinkSync(tempFile);

    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: review_design
 * 评审策划案
 */
export async function review_design(args, context) {
  try {
    const { content, doc_type = 'system' } = args;
    
    if (!content) {
      return { error: 'content is required' };
    }

    // 临时保存内容到文件
    const fs = await import('fs');
    const tempFile = path.join(SCRIPTS_DIR, 'temp_design.md');
    fs.writeFileSync(tempFile, content, 'utf-8');

    const result = await runPythonScript(REVIEWER, [tempFile, doc_type]);
    
    // 清理临时文件
    fs.unlinkSync(tempFile);

    return result;
  } catch (error) {
    return { error: error.message };
  }
}
export async function store_worldview(args) {
  try {
    const { category, content, importance = 0.9 } = args;
    
    if (!content) {
      return { error: 'content is required' };
    }

    const result = await runPythonScript(WORLDVIEW, [
      'store', category, content, importance.toString()
    ]);

    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: query_worldview
 * 查询世界观设定
 */
export async function query_worldview(args) {
  try {
    const { query, limit = 10 } = args;
    
    if (!query) {
      return { error: 'query is required' };
    }

    const result = await runPythonScript(WORLDVIEW, [
      'query', query, limit.toString()
    ]);

    return result;
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Tool: check_consistency
 * 检查世界观一致性
 */
export async function check_consistency(args) {
  try {
    const { content } = args;
    
    if (!content) {
      return { error: 'content is required' };
    }

    const result = await runPythonScript(WORLDVIEW, ['check', content]);

    return result;
  } catch (error) {
    return { error: error.message };
  }
}

// 导出所有工具
export default {
  generate_design,
  review_design,
  store_worldview,
  query_worldview,
  check_consistency
};
