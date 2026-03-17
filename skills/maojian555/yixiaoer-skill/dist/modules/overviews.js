import { getClient } from "../api/client.js";
function handleError(error) {
    const errorMsg = error.message;
    if (errorMsg.includes("登录已失效") || errorMsg.includes("请重新登录")) {
        return {
            success: false,
            message: `❌ ${errorMsg}，请重新调用 login 命令`,
        };
    }
    return {
        success: false,
        message: `❌ ${errorMsg}`,
    };
}
export async function getAccountOverviewsV2(params) {
    try {
        if (!params.platform) {
            return {
                success: false,
                message: "❌ 参数错误: 请提供 platform（平台中文名）",
            };
        }
        const client = getClient();
        const response = await client.getAccountOverviewsV2({
            platform: params.platform,
            page: params.page || 1,
            size: params.size || 10,
            name: params.name,
            group: params.group,
            loginStatus: params.loginStatus ?? 1,
        });
        if (!response.data || response.data.length === 0) {
            return {
                success: true,
                message: "暂无账号概览数据",
                data: response,
            };
        }
        let message = `📊 账号概览（${params.platform}）：共 ${response.totalSize} 条\n\n`;
        for (const item of response.data.slice(0, 10)) {
            message += `- ${item.platformName} / ${item.platformAccountName} / 负责人: ${item.principalName || "-"}\n`;
        }
        if (response.totalSize > 10) {
            message += `\n... 还有 ${response.totalSize - 10} 条`;
        }
        return {
            success: true,
            message,
            data: response,
        };
    }
    catch (error) {
        return handleError(error);
    }
}
export async function getContentOverviews(params) {
    try {
        const client = getClient();
        const response = await client.getContentOverviews({
            ...params,
            page: params.page || 1,
            size: params.size || 10,
        });
        if (!response.data || response.data.length === 0) {
            return {
                success: true,
                message: "暂无作品数据",
                data: response,
            };
        }
        let message = `📈 作品数据：共 ${response.totalSize} 条\n\n`;
        for (const item of response.data.slice(0, 10)) {
            message += `- ${item.accountName} / ${item.publishUserName} / 更新时间: ${item.updatedAt}\n`;
        }
        if (response.totalSize > 10) {
            message += `\n... 还有 ${response.totalSize - 10} 条`;
        }
        return {
            success: true,
            message,
            data: response,
        };
    }
    catch (error) {
        return handleError(error);
    }
}
//# sourceMappingURL=overviews.js.map