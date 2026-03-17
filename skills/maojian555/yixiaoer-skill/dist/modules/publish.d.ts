import type { GetPublishRecordsParams, SkillResult } from "../types.js";
export declare function getPublishRecords(params: GetPublishRecordsParams): Promise<SkillResult>;
export declare function publishContent(params: {
    /** 素材coverKey（上传后返回） */
    coverKey?: string;
    /** 发布描述 */
    desc?: string;
    /** 发布平台列表：抖音/小红书/知乎/B站/快手等 */
    platforms: string[];
    /** 内容类型：video-视频, article-文章, image-图文 */
    publishType: "video" | "article" | "imageText" | "image";
    /** 平台账号ID（从账号列表获取） */
    platformAccountId: string;
    /** 内容标题 */
    title: string;
    /** 内容正文 */
    description: string;
    /** 文章发布内容ID */
    publishContentId?: string;
    /** 创作类型 */
    createType?: number;
    /** 发布类型 */
    pubType?: number;
    /** 视频文件路径（本地路径或OSS URL） */
    videoPath?: string;
    /** 封面图片路径（本地路径或OSS URL） */
    coverPath?: string;
    /** 文章竖版封面路径（本地路径或URL） */
    verticalCoverPath?: string;
    /** 文章竖版封面key */
    verticalCoverKey?: string;
    /** 图片列表（图图文发布） */
    imagePaths?: string[];
    /** 视频文件大小（字节） */
    videoSize?: number;
    /** 视频时长（秒） */
    videoDuration?: number;
    /** 视频宽度 */
    videoWidth?: number;
    /** 视频高度 */
    videoHeight?: number;
    /** 封面图片大小（字节） */
    coverSize?: number;
    /** 竖版封面大小（字节） */
    verticalCoverSize?: number;
    /** 发布渠道：local-客户端发布, cloud-云发布 */
    publishChannel?: string;
    /** 客户端ID（云发布时需要） */
    clientId?: string;
    /** 代理ID（用于本机发布） */
    proxyId?: string;
    /** 封面宽度 */
    coverWidth?: number;
    /** 竖版封面宽度 */
    verticalCoverWidth?: number;
    /** 封面高度 */
    coverHeight?: number;
    /** 竖版封面高度 */
    verticalCoverHeight?: number;
}): Promise<SkillResult>;
//# sourceMappingURL=publish.d.ts.map