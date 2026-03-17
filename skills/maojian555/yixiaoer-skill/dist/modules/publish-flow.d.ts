import type { SkillResult } from "../types.js";
interface PublishFlowParams {
    username?: string;
    password?: string;
    teamId?: string;
    teamName?: string;
    platforms: string[];
    publishType: "video" | "article" | "imageText" | "image";
    platformAccountId: string;
    title: string;
    description: string;
    desc?: string;
    publishChannel?: string;
    clientId?: string;
    publishContentId?: string;
    createType?: number;
    pubType?: number;
    coverKey?: string;
    videoPath?: string;
    videoSize?: number;
    videoDuration?: number;
    videoWidth?: number;
    videoHeight?: number;
    coverPath?: string;
    verticalCoverPath?: string;
    verticalCoverKey?: string;
    imagePaths?: string[];
    coverSize?: number;
    verticalCoverSize?: number;
    coverWidth?: number;
    verticalCoverWidth?: number;
    coverHeight?: number;
    verticalCoverHeight?: number;
}
export declare function publishFlow(params: PublishFlowParams): Promise<SkillResult>;
export {};
//# sourceMappingURL=publish-flow.d.ts.map