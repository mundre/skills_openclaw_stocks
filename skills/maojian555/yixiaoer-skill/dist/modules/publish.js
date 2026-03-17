import { getClient } from "../api/client.js";
import { PLATFORM_RULES, validatePublishParams, buildContentPublishForm, } from "../config/platform-rules.js";
import * as fs from "fs";
import * as path from "path";
import axios from "axios";
import ffmpeg from "fluent-ffmpeg";
import ffmpegStatic from "ffmpeg-static";
let ffmpegPath;
if (ffmpegStatic) {
    ffmpeg.setFfmpegPath(ffmpegStatic);
    ffmpegPath = ffmpegStatic;
}
else {
    console.warn("⚠️ ffmpeg-static 未安装，视频封面提取功能将不可用");
    console.warn("💡 请运行: npm install ffmpeg-static");
}
/**
 * 根据关键词搜索并下载图片作为封面
 * @param keyword 搜索关键词
 * @param saveDir 保存目录
 * @returns 下载后的图片路径和大小
 */
async function searchAndDownloadCover(keyword, saveDir) {
    console.log(`🔍 正在搜索封面图片: ${keyword}`);
    // 确保目录存在
    if (!fs.existsSync(saveDir)) {
        fs.mkdirSync(saveDir, { recursive: true });
    }
    // 方法1: 使用 Unsplash Source (已失效，改用其他方式)
    // 方法2: 使用 Picsum 随机高质量图片
    const randomImageUrl = `https://picsum.photos/seed/${encodeURIComponent(keyword)}/1080/1920`;
    try {
        console.log(`🖼️ 尝试获取图片: ${randomImageUrl}`);
        const response = await axios.get(randomImageUrl, {
            responseType: 'arraybuffer',
            timeout: 30000,
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            maxRedirects: 5
        });
        const fileName = `cover_${Date.now()}.jpg`;
        const savePath = path.join(saveDir, fileName);
        fs.writeFileSync(savePath, Buffer.from(response.data));
        const stats = fs.statSync(savePath);
        console.log(`✅ 封面图片获取成功: ${savePath} (${stats.size} bytes)`);
        return {
            coverPath: savePath,
            coverSize: stats.size,
            width: 1080,
            height: 1920
        };
    }
    catch (error) {
        console.log(`❌ Picsum获取失败，尝试备用方案...`);
        // 备用: 使用固定的通用图片
        const fallbackUrl = 'https://picsum.photos/1080/1920';
        try {
            const response = await axios.get(fallbackUrl, {
                responseType: 'arraybuffer',
                timeout: 30000,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                maxRedirects: 5
            });
            const fileName = `cover_${Date.now()}.jpg`;
            const savePath = path.join(saveDir, fileName);
            fs.writeFileSync(savePath, Buffer.from(response.data));
            const stats = fs.statSync(savePath);
            console.log(`✅ 封面图片(备用)获取成功: ${savePath} (${stats.size} bytes)`);
            return {
                coverPath: savePath,
                coverSize: stats.size,
                width: 1080,
                height: 1920
            };
        }
        catch (fallbackError) {
            console.log(`❌ 备用方案也失败: ${fallbackError.message}`);
            throw fallbackError;
        }
    }
}
/**
 * 从视频中提取封面图片
 * @param videoPath 视频文件路径
 * @param width 封面宽度
 * @param height 封面高度
 * @returns 封面图片路径和大小
 */
async function extractVideoCover(videoPath, width = 1080, height = 1920) {
    if (!ffmpegPath) {
        throw new Error("❌ ffmpeg-static 未安装，无法提取视频封面\n" +
            "💡 请运行: npm install ffmpeg-static\n" +
            "📖 或者在发布时直接传入 coverPath 参数指定封面图片");
    }
    return new Promise((resolve, reject) => {
        // 安全处理路径 - 使用字符串操作代替 path 方法
        const lastSlash = Math.max(videoPath.lastIndexOf('/'), videoPath.lastIndexOf('\\'));
        const videoDir = lastSlash > 0 ? videoPath.substring(0, lastSlash) : '.';
        const fileName = lastSlash > 0 ? videoPath.substring(lastSlash + 1) : videoPath;
        const lastDot = fileName.lastIndexOf('.');
        const videoName = lastDot > 0 ? fileName.substring(0, lastDot) : fileName;
        const coverPath = path.join(videoDir, `${videoName}_cover.jpg`);
        console.log(`🎬 正在从视频提取封面: ${videoPath}`);
        ffmpeg(videoPath)
            .on("end", () => {
            console.log(`✅ 封面提取完成: ${coverPath}`);
            const stats = fs.statSync(coverPath);
            resolve({
                coverPath,
                coverSize: stats.size,
            });
        })
            .on("error", (err) => {
            console.error(`❌ 封面提取失败: ${err.message}`);
            reject(err);
        })
            .screenshots({
            timestamps: ["00:00:01"], // 第1秒
            folder: videoDir,
            filename: `${videoName}_cover.jpg`,
            size: `${width}x${height}`,
        });
    });
}
function normalizePlatform(input) {
    if (PLATFORM_RULES[input])
        return input;
    const fromName = Object.values(PLATFORM_RULES).find(rule => rule.name === input);
    if (fromName)
        return fromName.code;
    return null;
}
function normalizePublishType(input) {
    if (input === "image")
        return "imageText";
    if (input === "video" || input === "article" || input === "imageText")
        return input;
    return null;
}
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
async function uploadFileToOss(filePath, client) {
    const fileName = path.basename(filePath);
    const fileSize = fs.statSync(filePath).size;
    let contentType = "application/octet-stream";
    if (fileName.endsWith(".mp4"))
        contentType = "video/mp4";
    else if (fileName.endsWith(".jpg") || fileName.endsWith(".jpeg"))
        contentType = "image/jpeg";
    else if (fileName.endsWith(".png"))
        contentType = "image/png";
    else if (fileName.endsWith(".gif"))
        contentType = "image/gif";
    const uploadResult = await client.getUploadUrl(fileName, fileSize, contentType);
    const fileStream = fs.createReadStream(filePath);
    await axios.put(uploadResult.uploadUrl, fileStream, {
        headers: {
            "Content-Type": contentType,
            "Content-Length": fileSize,
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity,
    });
    return { key: uploadResult.fileKey, size: fileSize };
}
export async function getPublishRecords(params) {
    try {
        const client = getClient();
        const response = await client.getPublishRecords({
            page: params.page || 1,
            size: params.size || 20,
        });
        if (!response.data || response.data.length === 0) {
            return {
                success: true,
                message: "暂无发布记录",
                data: { list: [], total: 0 },
            };
        }
        let message = `📋 获取到 ${response.totalSize} 条发布记录:\n\n`;
        for (const record of response.data.slice(0, 10)) {
            const typeEmoji = record.publishType === "video" ? "🎬" : "📝";
            message += `${typeEmoji} ${record.title || "无标题"}\n`;
            message += `   平台: ${record.platforms?.join(", ") || "-"} | 账号: ${record.nickName || "-"}\n`;
            if (record.createdAt) {
                const date = new Date(record.createdAt);
                message += `   时间: ${date.toLocaleString()}\n`;
            }
            message += "\n";
        }
        if (response.totalSize > 10) {
            message += `... 还有 ${response.totalSize - 10} 条记录`;
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
export async function publishContent(params) {
    try {
        const client = getClient();
        if (!params.platforms || params.platforms.length === 0) {
            return {
                success: false,
                message: "❌ 参数错误: 请至少选择一个发布平台",
            };
        }
        const publishType = normalizePublishType(params.publishType);
        if (!publishType) {
            return {
                success: false,
                message: "❌ 参数错误: publishType 只支持 video/article/imageText/image",
            };
        }
        const publishChannel = params.publishChannel || "cloud";
        // 有 clientId 则是本机发布，没有则是云发布
        const finalPublishChannel = params.clientId ? "local" : publishChannel;
        // 本机发布需要 clientId
        if (finalPublishChannel === "local" && !params.clientId) {
            return {
                success: false,
                message: "❌ 参数错误: 本机发布需要提供 clientId（设备号）",
            };
        }
        if (publishType === "video" && !params.videoPath) {
            return {
                success: false,
                message: "❌ 参数错误: video 类型需要提供 videoPath",
            };
        }
        // 视频发布：封面地址必填校验
        if (publishType === "video" && !params.coverPath && !params.coverKey) {
            return {
                success: false,
                message: "❌ 参数错误: video 类型需要提供封面图片地址 (coverPath)",
            };
        }
        if (publishType === "imageText" && (!params.imagePaths || params.imagePaths.length === 0)) {
            return {
                success: false,
                message: "❌ 参数错误: imageText 类型需要提供 imagePaths",
            };
        }
        const platformForms = {};
        const platformCodes = [];
        for (const platformInput of params.platforms) {
            const platformCode = normalizePlatform(platformInput);
            if (!platformCode) {
                return {
                    success: false,
                    message: `❌ 不支持的平台: ${platformInput}`,
                };
            }
            platformCodes.push(platformCode);
            const rule = PLATFORM_RULES[platformCode];
            if (!rule) {
                return {
                    success: false,
                    message: `❌ 不支持的平台: ${platformInput}`,
                };
            }
            const validation = validatePublishParams(platformCode, publishType);
            if (!validation.valid) {
                return {
                    success: false,
                    message: `❌ 参数验证失败: ${validation.errors.join('; ')}`,
                };
            }
            const platformForm = { formType: "task" };
            const platformName = PLATFORM_RULES[platformCode]?.name;
            if (platformName) {
                platformForms[platformName] = platformForm;
            }
        }
        const contentPublishForm = buildContentPublishForm(publishType, {
            title: params.title,
            description: params.description,
            createType: params.createType,
            pubType: params.pubType,
        });
        const accountForm = {
            platformAccountId: params.platformAccountId,
            publishContentId: params.publishContentId,
            coverKey: params.coverKey,
            contentPublishForm,
            mediaId: "",
        };
        // 视频：远端 http 用 path，本地上传用 key
        if (publishType === "video" && params.videoPath) {
            // 检查是否是URL还是本地路径
            if (params.videoPath.startsWith('http')) {
                accountForm.video = {
                    path: params.videoPath,
                    duration: params.videoDuration || 0,
                    width: params.videoWidth || 1080,
                    height: params.videoHeight || 1920,
                    size: params.videoSize || 0,
                };
            }
            else {
                // 本地路径 - 自动上传到OSS
                console.log(`📤 正在上传视频到OSS: ${params.videoPath}`);
                const videoInfo = await uploadFileToOss(params.videoPath, client);
                console.log(`✅ 视频上传成功, key: ${videoInfo.key}`);
                accountForm.video = {
                    key: videoInfo.key,
                    duration: params.videoDuration || 0,
                    width: params.videoWidth || 1080,
                    height: params.videoHeight || 1920,
                    size: videoInfo.size,
                };
            }
        }
        // 文章发布：封面地址必填校验
        if (publishType === "article" && !params.coverPath && !params.coverKey) {
            return {
                success: false,
                message: "❌ 参数错误: article 类型需要提供封面图片地址 (coverPath 或 coverKey)",
            };
        }
        // 图文发布：如果未提供封面也没有图片，返回错误提示
        if (publishType === "imageText" && !params.coverPath && (!params.imagePaths || params.imagePaths.length === 0)) {
            return {
                success: false,
                message: "❌ 图文发布需要提供封面图片或图片列表，请提供 coverPath 或 imagePaths 参数",
            };
        }
        // 封面图片：远端 http 用 path，本地上传用 key
        if (params.coverPath) {
            if (params.coverPath.startsWith('http')) {
                if (publishType === "article") {
                    const covers = contentPublishForm.covers || [];
                    covers.push({
                        path: params.coverPath,
                        width: params.coverWidth || 0,
                        height: params.coverHeight || 0,
                        size: params.coverSize || 0,
                    });
                    contentPublishForm.covers = covers;
                    // 文章使用远端URL时，也需要设置 coverKey（虽然可能无效，但保持结构完整）
                    accountForm.coverKey = '';
                }
                else {
                    accountForm.cover = {
                        path: params.coverPath,
                        width: params.coverWidth || 1080,
                        height: params.coverHeight || 1920,
                        size: params.coverSize || 0,
                    };
                }
            }
            else {
                console.log(`📤 正在上传封面到OSS: ${params.coverPath}`);
                const coverInfo = await uploadFileToOss(params.coverPath, client);
                console.log(`✅ 封面上传成功, key: ${coverInfo.key}`);
                if (publishType === "article") {
                    const covers = contentPublishForm.covers || [];
                    covers.push({
                        key: coverInfo.key,
                        width: params.coverWidth || 0,
                        height: params.coverHeight || 0,
                        size: coverInfo.size,
                    });
                    contentPublishForm.covers = covers;
                    // 文章也需要设置 coverKey
                    accountForm.coverKey = coverInfo.key;
                }
                else {
                    accountForm.coverKey = coverInfo.key;
                    accountForm.cover = {
                        key: coverInfo.key,
                        width: params.coverWidth || 1080,
                        height: params.coverHeight || 1920,
                        size: coverInfo.size,
                    };
                }
            }
        }
        // 文章竖版封面：远端 http 用 path，本地上传用 key
        if (publishType === "article" && params.verticalCoverPath) {
            const verticalCovers = contentPublishForm.verticalCovers || [];
            if (params.verticalCoverPath.startsWith('http')) {
                verticalCovers.push({
                    path: params.verticalCoverPath,
                    width: params.verticalCoverWidth || 0,
                    height: params.verticalCoverHeight || 0,
                    size: params.verticalCoverSize || 0,
                });
            }
            else {
                console.log(`📤 正在上传竖版封面到OSS: ${params.verticalCoverPath}`);
                const verticalInfo = await uploadFileToOss(params.verticalCoverPath, client);
                console.log(`✅ 竖版封面上传成功, key: ${verticalInfo.key}`);
                verticalCovers.push({
                    key: verticalInfo.key,
                    width: params.verticalCoverWidth || 0,
                    height: params.verticalCoverHeight || 0,
                    size: verticalInfo.size,
                });
            }
            contentPublishForm.verticalCovers = verticalCovers;
        }
        // 文章封面/竖版封面直接传 key
        if (publishType === "article" && params.coverKey && !params.coverPath) {
            const covers = contentPublishForm.covers || [];
            covers.push({
                key: params.coverKey,
                width: params.coverWidth || 0,
                height: params.coverHeight || 0,
                size: params.coverSize || 0,
            });
            contentPublishForm.covers = covers;
        }
        if (publishType === "article" && params.verticalCoverKey && !params.verticalCoverPath) {
            const verticalCovers = contentPublishForm.verticalCovers || [];
            verticalCovers.push({
                key: params.verticalCoverKey,
                width: params.verticalCoverWidth || 0,
                height: params.verticalCoverHeight || 0,
                size: params.verticalCoverSize || 0,
            });
            contentPublishForm.verticalCovers = verticalCovers;
        }
        // 图文图片：远端 http 用 path，本地上传用 key
        if (publishType === "imageText" && params.imagePaths && params.imagePaths.length > 0) {
            const imageObjects = [];
            for (const imagePath of params.imagePaths) {
                if (imagePath.startsWith('http')) {
                    imageObjects.push({
                        path: imagePath,
                        width: params.coverWidth || 1080,
                        height: params.coverHeight || 1920,
                        size: params.coverSize || 0,
                    });
                }
                else {
                    console.log(`📤 正在上传图片到OSS: ${imagePath}`);
                    const imageInfo = await uploadFileToOss(imagePath, client);
                    console.log(`✅ 图片上传成功, key: ${imageInfo.key}`);
                    imageObjects.push({
                        key: imageInfo.key,
                        width: params.coverWidth || 1080,
                        height: params.coverHeight || 1920,
                        size: imageInfo.size,
                    });
                }
            }
            accountForm.images = imageObjects;
            // 若未显式传封面，默认使用第一张图作为封面
            if (!accountForm.coverKey && imageObjects.length > 0) {
                const first = imageObjects[0];
                if (first.key)
                    accountForm.coverKey = first.key;
                accountForm.cover = {
                    key: first.key,
                    path: first.path,
                    width: first.width,
                    height: first.height,
                    size: first.size,
                };
            }
        }
        // 构建发布参数
        // platforms 使用平台中文名数组
        const platformNames = platformCodes.map(code => PLATFORM_RULES[code]?.name).filter(Boolean);
        let publishArgs = {
            clientId: params.clientId || "",
            platforms: platformNames, // 使用平台中文名数组
            publishType,
            publishChannel: finalPublishChannel,
            coverKey: accountForm.coverKey || '',
            proxyId: params.proxyId,
            publishArgs: {
                accountForms: [accountForm],
                platformForms,
                content: publishType !== "video" ? params.description : undefined,
            },
        };
        let response;
        let isLocalPublish = finalPublishChannel === "local";
        try {
            // 尝试发布
            response = await client.publishTask(publishArgs);
        }
        catch (error) {
            // 检测代理未设置错误，自动转为本机发布
            const errorMsg = error.message || '';
            console.log('📛 发布错误:', errorMsg);
            if (errorMsg.includes('代理未设置') && params.clientId) {
                console.log('⚠️ 云发布失败，检测到代理未设置，准备转为本机发布...');
                isLocalPublish = true;
                // 本机发布：使用 clientId 作为设备标识，设置 publishChannel 为 local
                publishArgs = {
                    clientId: params.clientId, // 设备号
                    platforms: platformNames, // 使用平台中文名数组
                    publishType,
                    publishChannel: 'local', // 本机发布
                    coverKey: accountForm.coverKey || '',
                    publishArgs: {
                        accountForms: [accountForm],
                        platformForms,
                        content: publishType !== "video" ? params.description : undefined,
                    },
                };
                console.log('🔄 正在重试本机发布...');
                response = await client.publishTask(publishArgs);
            }
            else {
                throw error;
            }
        }
        const platformNamesStr = platformCodes
            .map(code => PLATFORM_RULES[code]?.name || code)
            .join(", ");
        const publishMode = isLocalPublish ? '本机发布' : '云发布';
        return {
            success: true,
            message: `✅ ${publishMode}任务已提交到 ${platformNamesStr}`,
            data: response,
        };
    }
    catch (error) {
        return handleError(error);
    }
}
//# sourceMappingURL=publish.js.map