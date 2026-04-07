/**
 * 文件信息接口
 */
interface FileInfo {
    name: string;
    path: string;
    size: number;
    type: string;
}
/**
 * 技能参数接口
 */
interface SkillParameters {
    file: FileInfo;
    instruction: string;
    apiKey?: string;
}
/**
 * 技能上下文接口
 */
interface SkillContext {
    parameters: SkillParameters;
}
/**
 * AI 文件脱敏技能
 */
declare class AIRedactionSkill {
    private readonly API_BASE_URL;
    private readonly WEBSITE_URL;
    constructor();
    /**
     * 验证文件
     */
    private validateFile;
    /**
     * 验证脱敏指令
     */
    private validateInstruction;
    /**
     * 调用脱敏 API 上传文件并创建任务
     */
    private uploadAndCreateTask;
    /**
     * 执行文件脱敏
     */
    execute(context: SkillContext): Promise<{
        taskUrl: string;
    }>;
}
declare const _default: AIRedactionSkill;
export default _default;
