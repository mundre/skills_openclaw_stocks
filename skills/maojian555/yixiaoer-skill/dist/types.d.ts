export interface YixiaoerConfig {
    baseUrl?: string;
}
export interface LoginResponse {
    token: string;
    expiresIn?: number;
    user: {
        id: string;
        username: string;
        nickname?: string;
        avatar?: string;
    };
}
export interface MediaAccount {
    id?: string;
    platformName: string;
    platformAvatar: string;
    platformAccountName: string;
    platformType: number;
    platformCode?: string;
    proxyId?: string;
    remark?: string;
    accountId?: string;
}
export interface TeamInfo {
    id: string;
    name: string;
    logoUrl: string;
    isVip: boolean;
    expiredAt: number;
}
export interface ApiResponse<T = any> {
    statusCode: number;
    data: T;
    message?: string;
}
export interface SkillResult<T = any> {
    success: boolean;
    message: string;
    data?: T;
}
export interface LoginParams {
    username: string;
    password: string;
}
export interface ListAccountsParams {
    page?: number;
    size?: number;
    loginStatus?: number;
}
export interface GetPublishRecordsParams {
    page?: number;
    size?: number;
}
export interface UploadUrlParams {
    fileName: string;
    fileSize: number;
    contentType: string;
}
export interface UploadUrlResult {
    uploadUrl: string;
    fileKey: string;
}
export interface AccountOverviewsParams {
    platform: string;
    page?: number;
    size?: number;
    name?: string;
    group?: string;
    loginStatus?: number;
}
export interface ContentOverviewsParams {
    platformAccountId?: string;
    publishUserId?: string;
    platform?: string;
    type?: "all" | "video" | "miniVideo" | "dynamic" | "article";
    title?: string;
    publishStartTime?: number;
    publishEndTime?: number;
    page?: number;
    size?: number;
}
//# sourceMappingURL=types.d.ts.map