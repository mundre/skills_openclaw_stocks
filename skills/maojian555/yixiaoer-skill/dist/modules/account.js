import { createClient, getClient, clearClient } from '../api/client.js';
export async function login(params) {
    try {
        const { username, password } = params;
        if (!username || !password) {
            return {
                success: false,
                message: '❌ 参数错误: 请提供用户名和密码'
            };
        }
        const client = createClient();
        const result = await client.login(username, password);
        return {
            success: true,
            message: `✅ 登录成功！`,
            data: {
                token: result.token,
                expiresIn: result.expiresIn
            }
        };
    }
    catch (error) {
        return {
            success: false,
            message: `❌ 登录失败: ${error.message}`
        };
    }
}
export async function logout() {
    try {
        clearClient();
        return {
            success: true,
            message: '✅ 已退出登录'
        };
    }
    catch (error) {
        return {
            success: false,
            message: `❌ 退出登录失败: ${error.message}`
        };
    }
}
export async function listAccounts(params) {
    try {
        const client = getClient();
        const response = await client.getAccounts({
            page: params.page || 1,
            size: params.size || 20,
            loginStatus: 1
        });
        if (!response.data || response.data.length === 0) {
            return {
                success: true,
                message: '暂无绑定的自媒体账号',
                data: { list: [], total: 0 }
            };
        }
        const platformSummary = {};
        for (const account of response.data) {
            const platform = account.platformName;
            platformSummary[platform] = (platformSummary[platform] || 0) + 1;
        }
        let message = `📋 共获取到 ${response.totalSize} 个账号（仅展示登录有效账号）:\n\n`;
        for (const [platform, count] of Object.entries(platformSummary)) {
            message += `- ${platform}: ${count} 个\n`;
        }
        message += '\n📝 账号详情:\n';
        for (const account of response.data.slice(0, 10)) {
            message += `- ${account.platformName} - ${account.platformAccountName}\n`;
            message += `  ID: ${account.id || account.accountId}\n`;
        }
        if (response.totalSize > 10) {
            message += `\n... 还有 ${response.totalSize - 10} 个账号`;
        }
        return {
            success: true,
            message,
            data: response
        };
    }
    catch (error) {
        const errorMsg = error.message;
        if (errorMsg.includes('登录已失效') || errorMsg.includes('请重新登录')) {
            return {
                success: false,
                message: `❌ ${errorMsg}，请重新调用 login 命令`
            };
        }
        return {
            success: false,
            message: `❌ 获取账号列表失败: ${errorMsg}`
        };
    }
}
export async function getTeams() {
    try {
        const client = getClient();
        const response = await client.getTeams();
        if (!response.data || response.data.length === 0) {
            return {
                success: true,
                message: '暂无团队',
                data: { list: [] }
            };
        }
        let message = `👥 共 ${response.data.length} 个团队:\n\n`;
        for (const team of response.data) {
            const vipStatus = team.isVip ? '✅ VIP' : '❌ 普通';
            message += `- ${team.name} (${vipStatus})\n`;
        }
        return {
            success: true,
            message,
            data: response
        };
    }
    catch (error) {
        const errorMsg = error.message;
        if (errorMsg.includes('登录已失效') || errorMsg.includes('请重新登录')) {
            return {
                success: false,
                message: `❌ ${errorMsg}，请重新调用 login 命令`
            };
        }
        return {
            success: false,
            message: `❌ 获取团队列表失败: ${errorMsg}`
        };
    }
}
//# sourceMappingURL=account.js.map