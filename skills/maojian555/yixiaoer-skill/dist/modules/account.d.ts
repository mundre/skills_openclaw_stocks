import type { ListAccountsParams, LoginParams, SkillResult } from '../types.js';
export declare function login(params: LoginParams): Promise<SkillResult>;
export declare function logout(): Promise<SkillResult>;
export declare function listAccounts(params: ListAccountsParams): Promise<SkillResult>;
export declare function getTeams(): Promise<SkillResult>;
//# sourceMappingURL=account.d.ts.map