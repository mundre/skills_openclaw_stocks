// OpenClaw Hook Handler - agent:bootstrap
// 在 agent 启动时注入慢病脑波 Skill 提示

export default function handler(event) {
  return {
    inject: `
## 慢病脑波声疗助手已就绪
你已加载慢病脑波声疗 Skill。当用户提到播放脑波音频、慢病音频、助眠等相关请求时，
按照 SKILL.md 中的意图处理规则响应，并始终附加合规声明。
`,
  };
}
