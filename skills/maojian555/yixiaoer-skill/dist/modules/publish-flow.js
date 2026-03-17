import { getClient } from "../api/client.js";
import * as account from "./account.js";
import * as publish from "./publish.js";
function resolveTeam(teams, teamId, teamName) {
    if (teamId) {
        const match = teams.find(t => t.id === teamId);
        return match || null;
    }
    if (teamName) {
        const match = teams.find(t => t.name === teamName);
        return match || null;
    }
    return null;
}
export async function publishFlow(params) {
    try {
        // Ensure login
        let client;
        try {
            client = getClient();
        }
        catch {
            if (!params.username || !params.password) {
                return {
                    success: false,
                    message: "❌ 请先登录或提供 username/password 执行发布流程",
                };
            }
            const loginResult = await account.login({
                username: params.username,
                password: params.password,
            });
            if (!loginResult.success)
                return loginResult;
            client = getClient();
        }
        // Ensure team selection
        if (!params.teamId && !params.teamName) {
            return {
                success: false,
                message: "❌ 请提供 teamId 或 teamName 以选择团队",
            };
        }
        const teamsResult = await account.getTeams();
        if (!teamsResult.success)
            return teamsResult;
        const teams = teamsResult.data?.data || [];
        const selected = resolveTeam(teams, params.teamId, params.teamName);
        if (!selected) {
            const names = teams.map((t) => t.name).join(" / ");
            return {
                success: false,
                message: `❌ 未找到匹配团队，请检查 teamId/teamName。可用团队: ${names || "无"}`,
            };
        }
        // Validate account exists (loginStatus=1)
        const accounts = await client.getAccounts({ page: 1, size: 200, loginStatus: 1 });
        const accountMatch = accounts.data?.find(a => a.id === params.platformAccountId);
        if (!accountMatch) {
            return {
                success: false,
                message: "❌ 未找到有效的 platformAccountId，请先用 list-accounts 获取登录有效账号\n" +
                    "💡 提示: platformAccountId 应为账号列表中的 id 字段值",
            };
        }
        return await publish.publishContent(params);
    }
    catch (error) {
        return {
            success: false,
            message: `❌ 发布流程执行失败: ${error.message}`,
        };
    }
}
//# sourceMappingURL=publish-flow.js.map