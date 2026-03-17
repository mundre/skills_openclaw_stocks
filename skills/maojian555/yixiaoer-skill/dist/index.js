import * as account from './modules/account.js';
import * as publish from './modules/publish.js';
import * as publishFlow from './modules/publish-flow.js';
import * as overviews from './modules/overviews.js';
import { getClient } from './api/client.js';
export default async function run(action, params) {
    try {
        switch (action) {
            case 'login':
                return await account.login(params);
            case 'logout':
                return await account.logout();
            case 'list-accounts':
                return await account.listAccounts(params);
            case 'get-teams':
                return await account.getTeams();
            case 'account-overviews':
                return await overviews.getAccountOverviewsV2(params);
            case 'content-overviews':
                return await overviews.getContentOverviews(params);
            case 'publish':
                return await publish.publishContent(params);
            case 'publish-flow':
                return await publishFlow.publishFlow(params);
            case 'get-publish-records':
                return await publish.getPublishRecords(params);
            case 'upload-url':
                return await getUploadUrl(params);
            default:
                return {
                    success: false,
                    message: `❌ 不支持的操作: ${action}\n\n支持的操作:\n- login: 用户名密码登录\n- logout: 退出登录\n- list-accounts: 获取账号列表\n- get-teams: 获取团队列表\n- account-overviews: 账号概览-新版\n- content-overviews: 作品数据列表\n- publish: 发布内容\n- publish-flow: 一键登录/选团队/发布\n- get-publish-records: 获取发布记录\n- upload-url: 获取上传URL`
                };
        }
    }
    catch (error) {
        return {
            success: false,
            message: `❌ 执行失败: ${error.message}`,
            data: null
        };
    }
}
async function getUploadUrl(params) {
    try {
        const client = getClient();
        if (!params.fileName) {
            return {
                success: false,
                message: "❌ 参数错误: 请提供 fileName (文件名)"
            };
        }
        if (!params.fileSize) {
            return {
                success: false,
                message: "❌ 参数错误: 请提供 fileSize (文件大小)"
            };
        }
        if (!params.contentType) {
            return {
                success: false,
                message: "❌ 参数错误: 请提供 contentType (文件类型，如 video/mp4)"
            };
        }
        const result = await client.getUploadUrl(params.fileName, params.fileSize, params.contentType);
        return {
            success: true,
            message: `✅ 获取上传URL成功\n\n上传URL: ${result.uploadUrl}\n文件Key: ${result.fileKey}`,
            data: result
        };
    }
    catch (error) {
        return {
            success: false,
            message: `❌ 获取上传URL失败: ${error.message}`,
            data: null
        };
    }
}
//# sourceMappingURL=index.js.map