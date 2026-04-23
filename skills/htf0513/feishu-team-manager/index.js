/**
 * 飞书团队管理器 - 核心调度逻辑 (v2.3)
 * 实现主 Agent 拦截、HR 自动化安装、技能平移与环境验证
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

async function main() {
    const configPath = path.join(process.env.HOME || '/root', '.openclaw/openclaw.json');
    if (!fs.existsSync(configPath)) {
        process.exit(1);
    }

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const agents = config.agents?.list || [];
    const hrAgent = agents.find(a => a.id === 'hr_recruiter');

    // 获取当前技能所在目录
    const skillSourcePath = __dirname;

    // --- 自动化安装/修复逻辑 ---
    if (!hrAgent) {
        console.log("拦截：检测到尚未创建 HR Agent。正在启动自动化部署流程...");
        
        try {
            // 1. 创建 HR 工作空间
            const hrWorkspace = path.join(process.env.HOME || '/root', '.openclaw/hr_recruiter_workspace');
            if (!fs.existsSync(hrWorkspace)) {
                console.log(`正在创建 HR 工作空间: ${hrWorkspace}`);
                execSync(`mkdir -p ${hrWorkspace}/skills`);
            }

            // 2. 注入身份文件 (从模板读取)
            console.log("正在注入 HR 身份 (IDENTITY/SOUL/AGENTS)...");
            const templates = ['identity', 'soul', 'agents'];
            templates.forEach(t => {
                const src = path.join(skillSourcePath, 'assets/templates', `hr_${t}.md`);
                const dst = path.join(hrWorkspace, `${t.toUpperCase()}.md`);
                if (fs.existsSync(src)) {
                    execSync(`cp ${src} ${dst}`);
                }
            });

            // 3. 技能平移 (Migration)
            console.log("正在将 feishu-team-manager 平移至 HR 空间...");
            const targetSkillPath = path.join(hrWorkspace, 'skills/feishu-team-manager');
            execSync(`rm -rf ${targetSkillPath}`); // 清理旧数据确保一致性
            execSync(`mkdir -p ${targetSkillPath}`);
            execSync(`cp -r ${skillSourcePath}/* ${targetSkillPath}/`);

            // 4. 注册 Agent 到配置
            console.log("正在将 hr_recruiter 注册到 openclaw.json...");
            execSync(`openclaw agents add hr_recruiter --workspace ${hrWorkspace}`);

            console.log("✅ HR 部署完成。");
        } catch (error) {
            console.error("❌ 部署失败:", error.message);
            return;
        }
        
        console.log("--- 引导提示 ---");
        console.log("主人，HR 大姐头已入职并配置了专属工作空间。");
        console.log("由于环境变更，请运行 `openclaw gateway restart` 生效。");
        return;
    }

    // --- 正常运行逻辑 ---
    const currentAgentId = process.env.OPENCLAW_AGENT_ID || 'main';
    
    if (currentAgentId === 'main') {
        console.log("检测到 HR Agent (小唐) 已就绪。管理功能已委托。");
        console.log("若您修改了管理技能，我会自动同步更新 HR 的独立空间。");
        
        // 自动同步更新逻辑
        const hrWorkspace = hrAgent.workspace;
        if (hrWorkspace && fs.existsSync(hrWorkspace)) {
            const targetSkillPath = path.join(hrWorkspace, 'skills/feishu-team-manager');
            execSync(`cp -r ${skillSourcePath}/* ${targetSkillPath}/`);
        }
    } else if (currentAgentId === 'hr_recruiter') {
        console.log("✅ 大姐头身份确认。正在加载管理与招聘工具...");
    }
}

main();
