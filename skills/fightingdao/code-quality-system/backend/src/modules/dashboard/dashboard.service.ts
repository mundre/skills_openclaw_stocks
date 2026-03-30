import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../common/prisma.service';
import { PeriodQueryDto } from '../../common/dto/common.dto';

@Injectable()
export class DashboardService {
  constructor(private prisma: PrismaService) {}

  /**
   * 获取大盘统计数据
   */
  async getOverview(dto: PeriodQueryDto) {
    const teamStats = await this.prisma.teamStatistic.findMany({
      where: {
        periodType: dto.periodType,
        periodValue: dto.periodValue,
      },
    });

    const overview = {
      totalMembers: teamStats.reduce((sum, s) => sum + s.totalMembers, 0),
      totalCommits: teamStats.reduce((sum, s) => sum + s.totalCommits, 0),
      totalTasks: teamStats.reduce((sum, s) => sum + s.totalTasks, 0),
      avgQualityScore: this.calculateAverageScore(
        // 只计算有提交的团队的分数
        teamStats
          .filter((s) => s.totalCommits > 0 && s.avgQualityScore !== null && Number(s.avgQualityScore) > 0)
          .map((s) => Number(s.avgQualityScore)),
      ),
    };

    return {
      success: true,
      data: overview,
    };
  }

  /**
   * 获取各小组整体分析报告
   */
  async getTeamDashboards(dto: PeriodQueryDto) {
    const teams = await this.prisma.team.findMany({
      include: {
        statistics: {
          where: {
            periodType: dto.periodType,
            periodValue: dto.periodValue,
          },
        },
      },
    });

    const dashboards = teams.map((team) => {
      const stat = team.statistics[0];
      return {
        id: team.id,
        name: team.name,
        leader: team.leaderName,
        totalMembers: stat?.totalMembers || 0,
        activeMembers: stat?.activeMembers || 0,
        totalCommits: stat?.totalCommits || 0,
        totalTasks: stat?.totalTasks || 0,
        insertions: stat?.totalInsertions || 0,
        deletions: stat?.totalDeletions || 0,
        avgQualityScore: stat?.avgQualityScore || null,
      };
    });

    return {
      success: true,
      data: dashboards,
    };
  }

  /**
   * 获取项目维度分析列表 - 用于项目概览
   * 按项目聚合：一个项目一条记录
   */
  async getProjectAnalysisList(dto: PeriodQueryDto & {
    page?: number;
    limit?: number;
    projectId?: string;
    version?: string;
    userName?: string;
  }) {
    // 构建查询条件
    const where: any = {
      periodType: dto.periodType,
      periodValue: dto.periodValue,
    };

    if (dto.projectId) {
      where.projectId = dto.projectId;
    }
    // 版本号精确匹配
    if (dto.version) {
      where.OR = [
        { branch: dto.version },
        { currentVersion: dto.version },
      ];
    }
    // 贡献者筛选
    if (dto.userName) {
      where.user = { username: { contains: dto.userName, mode: 'insensitive' } };
    }

    // 获取原始数据
    const allAnalyses = await this.prisma.codeAnalysis.findMany({
      where,
      include: {
        user: {
          include: { team: true }
        },
        project: true,
      },
    });

    // 按 projectId 聚合
    const projectMap = new Map<string, {
      projectId: string;
      projectName: string;
      branch: string;
      compareVersion: string;
      commitCount: number;
      insertions: number;
      deletions: number;
      contributors: { userId: string; userName: string }[];
    }>();

    for (const analysis of allAnalyses) {
      const projectId = analysis.projectId;
      
      if (!projectMap.has(projectId)) {
        projectMap.set(projectId, {
          projectId,
          projectName: analysis.project.name,
          branch: analysis.branch || analysis.currentVersion || '',
          compareVersion: analysis.compareVersion || '',
          commitCount: 0,
          insertions: 0,
          deletions: 0,
          contributors: [],
        });
      }

      const projectData = projectMap.get(projectId)!;
      
      // 累加数据
      projectData.commitCount += analysis.commitCount;
      projectData.insertions += analysis.insertions;
      projectData.deletions += analysis.deletions;
      
      // 添加贡献者（去重）
      const exists = projectData.contributors.some(c => c.userId === analysis.userId);
      if (!exists && analysis.user) {
        projectData.contributors.push({
          userId: analysis.userId,
          userName: analysis.user.username,
        });
      }
    }

    // 转换为数组
    let items = Array.from(projectMap.values()).map(data => ({
      id: data.projectId,
      ...data,
    }));

    // 分页
    const page = Number(dto.page) || 1;
    const limit = Number(dto.limit) || 10;
    const skip = (page - 1) * limit;
    const total = items.length;
    const paginatedItems = items.slice(skip, skip + limit);

    return {
      success: true,
      data: paginatedItems,
      meta: {
        total,
        page,
        limit,
        hasMore: total > page * limit,
      },
    };
  }

  /**
   * 获取代码分析列表 - 支持筛选和排序
   * 按人员维度聚合：一个人多个项目合并为一条记录
   */
  async getCodeAnalysisList(dto: PeriodQueryDto & {
    page?: number;
    limit?: number;
    teamId?: string;
    projectId?: string;
    userName?: string;
    version?: string;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }) {
    const page = Number(dto.page) || 1;
    const limit = Number(dto.limit) || 10;
    const skip = (page - 1) * limit;

    // 构建查询条件
    const where: any = {
      periodType: dto.periodType,
      periodValue: dto.periodValue,
    };

    // 筛选条件
    if (dto.teamId) {
      where.user = { teamId: dto.teamId };
    }
    if (dto.projectId) {
      where.projectId = dto.projectId;
    }
    if (dto.userName) {
      if (!where.user) where.user = {};
      where.user.username = { contains: dto.userName, mode: 'insensitive' };
    }
    // 版本筛选暂时保留但不生效（前端已注释）
    // if (dto.version) {
    //   where.OR = [
    //     { branch: { contains: dto.version, mode: 'insensitive' } },
    //     { currentVersion: { contains: dto.version, mode: 'insensitive' } },
    //   ];
    // }

    // 先获取所有符合条件的数据，然后在内存中按用户聚合
    const allAnalyses = await this.prisma.codeAnalysis.findMany({
      where,
      include: {
        user: {
          include: { team: true }
        },
        project: true,
      },
    });

    // 按 userId 聚合
    const userMap = new Map<string, {
      userId: string;
      userName: string;
      teamId: string;
      teamName: string;
      projects: { id: string; name: string }[];
      insertions: number;
      deletions: number;
      commitCount: number;
      taskCount: number;
      qualityScores: number[];
    }>();

    for (const analysis of allAnalyses) {
      const userId = analysis.userId;
      
      if (!userMap.has(userId)) {
        userMap.set(userId, {
          userId,
          userName: analysis.user.username,
          teamId: analysis.user.teamId || '',
          teamName: analysis.user.team?.name || '',
          projects: [],
          insertions: 0,
          deletions: 0,
          commitCount: 0,
          taskCount: 0,
          qualityScores: [],
        });
      }

      const userData = userMap.get(userId)!;
      
      // 添加项目（去重）
      const projectExists = userData.projects.some(p => p.id === analysis.projectId);
      if (!projectExists) {
        userData.projects.push({
          id: analysis.projectId,
          name: analysis.project.name,
        });
      }
      
      // 累加数据
      userData.insertions += analysis.insertions;
      userData.deletions += analysis.deletions;
      userData.commitCount += analysis.commitCount;
      userData.taskCount += analysis.taskCount || 0;
      
      // 收集质量分数
      if (analysis.aiQualityScore) {
        userData.qualityScores.push(Number(analysis.aiQualityScore));
      }
    }

    // 转换为数组并计算平均质量分
    let items = Array.from(userMap.values()).map(userData => {
      // 计算平均质量分
      const avgScore = userData.qualityScores.length > 0
        ? userData.qualityScores.reduce((a, b) => a + b, 0) / userData.qualityScores.length
        : null;

      // 按项目名排序
      const sortedProjects = userData.projects.sort((a, b) => a.name.localeCompare(b.name));

      return {
        id: userData.userId,
        userName: userData.userName,
        userId: userData.userId,
        teamName: userData.teamName,
        teamId: userData.teamId,
        projectName: sortedProjects.map(p => p.name).join('、'),
        projectIds: sortedProjects.map(p => p.id),
        projectId: sortedProjects[0]?.id || '', // 排序后的第一个项目
        insertions: userData.insertions,
        deletions: userData.deletions,
        commitCount: userData.commitCount,
        totalTasks: userData.taskCount,
        aiQualityScore: avgScore ? avgScore.toFixed(1) : null,
        qualityLevel: this.getQualityLevel(avgScore),
      };
    });

    // 排序
    const sortBy = dto.sortBy || 'insertions';
    const sortOrder = dto.sortOrder || 'desc';
    
    items.sort((a, b) => {
      let aVal: number, bVal: number;
      
      switch (sortBy) {
        case 'insertions':
          aVal = a.insertions;
          bVal = b.insertions;
          break;
        case 'deletions':
          aVal = a.deletions;
          bVal = b.deletions;
          break;
        case 'commitCount':
          aVal = a.commitCount;
          bVal = b.commitCount;
          break;
        case 'totalTasks':
          aVal = a.totalTasks;
          bVal = b.totalTasks;
          break;
        case 'aiQualityScore':
          aVal = a.aiQualityScore ? parseFloat(a.aiQualityScore) : 0;
          bVal = b.aiQualityScore ? parseFloat(b.aiQualityScore) : 0;
          break;
        default:
          aVal = a.insertions;
          bVal = b.insertions;
      }
      
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });

    // 分页
    const total = items.length;
    const paginatedItems = items.slice(skip, skip + limit);

    return {
      success: true,
      data: paginatedItems,
      meta: {
        total,
        page,
        limit,
        hasMore: total > page * limit,
      },
    };
  }

  /**
   * 获取质量等级
   */
  private getQualityLevel(score: number | null): string {
    if (score === null) return '良好';
    if (score >= 9) return '优秀';
    if (score >= 7) return '良好';
    if (score >= 5) return '一般';
    return '较差';
  }

  /**
   * 获取筛选选项数据
   */
  async getFilterOptions(dto: PeriodQueryDto) {
    // 获取该周期下的所有分析数据
    const analyses = await this.prisma.codeAnalysis.findMany({
      where: {
        periodType: dto.periodType,
        periodValue: dto.periodValue,
      },
      include: {
        user: {
          include: { team: true }
        },
        project: true,
      },
    });

    // 提取唯一的小组（从用户获取）
    const teamsMap = new Map();
    analyses.forEach(a => {
      if (a.user.team) {
        teamsMap.set(a.user.team.id, {
          id: a.user.team.id,
          name: a.user.team.name,
        });
      }
    });

    // 提取唯一的项目
    const projectsMap = new Map();
    analyses.forEach(a => {
      projectsMap.set(a.project.id, {
        id: a.project.id,
        name: a.project.name,
      });
    });

    // 提取唯一的成员
    const usersMap = new Map();
    analyses.forEach(a => {
      usersMap.set(a.user.id, {
        id: a.user.id,
        name: a.user.username,
      });
    });

    // 提取唯一的版本（分支名），过滤掉 origin/ 开头的远端分支
    const versionsSet = new Set<string>();
    analyses.forEach(a => {
      // 优先使用 currentVersion，过滤掉 origin/ 开头的
      if (a.currentVersion && !a.currentVersion.startsWith('origin/')) {
        versionsSet.add(a.currentVersion);
      }
      // 如果 branch 不是 origin/ 开头，也添加
      if (a.branch && !a.branch.startsWith('origin/') && !versionsSet.has(a.branch)) {
        versionsSet.add(a.branch);
      }
    });

    return {
      success: true,
      data: {
        teams: Array.from(teamsMap.values()),
        projects: Array.from(projectsMap.values()),
        users: Array.from(usersMap.values()),
        versions: Array.from(versionsSet).map(v => ({ value: v, label: v })),
      },
    };
  }

  /**
   * 计算平均分
   */
  private calculateAverageScore(scores: any[]): number | null {
    if (scores.length === 0) {
      return null;
    }
    const sum = scores.reduce((acc, score) => acc + Number(score), 0);
    return Math.round((sum / scores.length) * 100) / 100;
  }
}