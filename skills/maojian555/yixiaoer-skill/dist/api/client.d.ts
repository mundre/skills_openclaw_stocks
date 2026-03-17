import type { YixiaoerConfig, LoginResponse, MediaAccount, TeamInfo } from '../types.js';
export declare class YixiaoerClient {
    private client;
    private config;
    private accessToken;
    constructor(config: YixiaoerConfig);
    private loginInternal;
    request<T = any>(method: string, endpoint: string, data?: any): Promise<T>;
    login(username: string, password: string): Promise<LoginResponse>;
    logout(): void;
    isLoggedIn(): boolean;
    getTeams(): Promise<{
        data: TeamInfo[];
    }>;
    getAccounts(params?: {
        page?: number;
        size?: number;
        loginStatus?: number;
    }): Promise<{
        data: MediaAccount[];
        totalSize: number;
        page: number;
        size: number;
    }>;
    getAccountOverviewsV2(params: {
        platform: string;
        page?: number;
        size?: number;
        name?: string;
        group?: string;
        loginStatus?: number;
    }): Promise<{
        data: any[];
        page: number;
        size: number;
        totalSize: number;
        totalPage: number;
    }>;
    getContentOverviews(params?: {
        platformAccountId?: string;
        publishUserId?: string;
        platform?: string;
        type?: "all" | "video" | "miniVideo" | "dynamic" | "article";
        title?: string;
        publishStartTime?: number;
        publishEndTime?: number;
        page?: number;
        size?: number;
    }): Promise<{
        data: any[];
        headData: Array<{
            name: string;
            key: string;
        }>;
        page: number;
        size: number;
        totalSize: number;
        totalPage: number;
    }>;
    getPublishRecords(params?: {
        page?: number;
        size?: number;
    }): Promise<any>;
    publishTask(taskData: any): Promise<any>;
    getUploadUrl(fileName: string, fileSize: number, contentType: string): Promise<{
        uploadUrl: string;
        fileKey: string;
    }>;
    setAccessToken(token: string): void;
    getAccessToken(): string | null;
}
export declare function getClient(): YixiaoerClient;
export declare function createClient(baseUrl?: string): YixiaoerClient;
export declare function clearClient(): void;
//# sourceMappingURL=client.d.ts.map