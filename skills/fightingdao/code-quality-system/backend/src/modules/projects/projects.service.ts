import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../common/prisma.service';
import {
  ProjectListQueryDto,
  ProjectReportQueryDto,
} from './dto/projects.dto';

@Injectable()
export class ProjectsService {
  constructor(private prisma: PrismaService) {}

  /**
   * 获取项目列表
   */
  async getProjectList(dto: ProjectListQueryDto) {
    const page = dto.page || 1;
    const limit = dto.limit || 10;
    const skip = (page - 1) * limit;

    const where: any = {};
    if (dto.teamId) {
      where.teamId = dto.teamId;
    }
    if (dto.isActive !== undefined) {
      where.isActive = dto.isActive;
    }

    const [projects, total] = await Promise.all([
      this.prisma.project.findMany({
        where,
        skip,
        take: limit,
        include: {
          team: true,
        },
        orderBy: {
          createdAt: 'desc',
        },
      }),
      this.prisma.project.count({ where }),
    ]);

    const items = projects.map((project) => ({
      id: project.id,
      name: project.name,
      repository: project.repository,
      description: project.description,
      teamId: project.teamId,
      teamName: project.team?.name,
      techStack: project.techStack,
      isActive: project.isActive,
      defaultBranch: project.defaultBranch,
      lastCommitAt: project.lastCommitAt,
      createdAt: project.createdAt,
      updatedAt: project.updatedAt,
    }));

    return {
      success: true,
      data: items,
      meta: {
        total,
        page,
        limit,
        hasMore: total > page * limit,
      },
    };
  }

  /**
   * 解析项目 ID（支持 UUID、项目 ID 或项目名称）
   */
  private async resolveProjectId(idOrName: string): Promise<{ id: string; project: any } | null> {
    // 检查是否是 UUID 格式
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    
    if (uuidRegex.test(idOrName)) {
      // UUID 格式，直接按 ID 查找
      const project = await this.prisma.project.findUnique({
        where: { id: idOrName },
        include: { team: true },
      });
      return project ? { id: project.id, project } : null;
    }
    
    // 非 UUID 格式，先按 ID 查找，再按名称查找
    const projectById = await this.prisma.project.findUnique({
      where: { id: idOrName },
      include: { team: true },
    });
    
    if (projectById) {
      return { id: projectById.id, project: projectById };
    }
    
    // 按名称查找
    const projectByName = await this.prisma.project.findFirst({
      where: { name: idOrName },
      include: { team: true },
    });
    
    return projectByName ? { id: projectByName.id, project: projectByName } : null;
  }

  /**
   * 获取项目信息（支持 UUID、项目 ID 或项目名称）
   */
  async getProjectInfo(idOrName: string) {
    const result = await this.resolveProjectId(idOrName);
    
    if (!result) {
      throw new NotFoundException(`项目不存在: ${idOrName}`);
    }
    
    const project = result.project;

    return {
      success: true,
      data: {
        id: project.id,
        name: project.name,
        repository: project.repository,
        description: project.description,
        teamId: project.teamId,
        teamName: project.team?.name,
        techStack: project.techStack,
        isActive: project.isActive,
        defaultBranch: project.defaultBranch,
        lastCommitAt: project.lastCommitAt,
        createdAt: project.createdAt,
        updatedAt: project.updatedAt,
      },
    };
  }

  /**
   * 获取项目报告（支持 UUID、项目 ID 或项目名称）
   */
  async getProjectReport(idOrName: string, dto: ProjectReportQueryDto) {
    // 获取项目基本信息
    const result = await this.resolveProjectId(idOrName);

    if (!result) {
      throw new NotFoundException(`项目不存在: ${idOrName}`);
    }
    
    const project = result.project;

    const id = project.id;

    const periodType: 'week' | 'month' | 'quarter' = dto.periodType || 'week';
    const periodValue: string = dto.periodValue || this.getDefaultPeriodValue(periodType);

    // 获取项目统计数据
    const statistic = await this.prisma.projectStatistic.findUnique({
      where: {
        projectId_periodType_periodValue: {
          projectId: id,
          periodType,
          periodValue,
        },
      },
    });

    // 获取项目的成员分析数据
    const memberAnalyses = await this.prisma.codeAnalysis.findMany({
      where: {
        projectId: id,
        periodType,
        periodValue,
      },
      include: {
        user: true,
      },
      orderBy: { commitCount: 'desc' }
    });

    // 计算总提交次数和总问题数
    const totalCommits = memberAnalyses.reduce((sum, a) => sum + a.commitCount, 0);
    const totalIssues = await this.prisma.$queryRaw`
      SELECT COUNT(*) as count
      FROM code_issues ci
      JOIN code_analyses ca ON ci.analysis_id = ca.id
      WHERE ca.project_id = ${id}
        AND ca.period_type = ${periodType}
        AND ca.period_value = ${periodValue}
    ` as any[];
    const totalIssueCount = Number(totalIssues[0]?.count || 0);

    // 获取每个成员的问题统计
    const memberIssues = await this.prisma.$queryRaw`
      SELECT 
        ca.user_id,
        ci.severity,
        COUNT(*) as count
      FROM code_issues ci
      JOIN code_analyses ca ON ci.analysis_id = ca.id
      WHERE ca.project_id = ${id}
        AND ca.period_type = ${periodType}
        AND ca.period_value = ${periodValue}
      GROUP BY ca.user_id, ci.severity
    ` as any[];

    // 构建成员问题统计 Map
    const memberIssueMap = new Map<string, { p0: number; p1: number; p2: number; total: number }>();
    memberIssues.forEach((item: any) => {
      const userId = item.user_id;
      if (!memberIssueMap.has(userId)) {
        memberIssueMap.set(userId, { p0: 0, p1: 0, p2: 0, total: 0 });
      }
      const stats = memberIssueMap.get(userId)!;
      stats.total += Number(item.count);
      if (item.severity === 'P0') stats.p0 += Number(item.count);
      else if (item.severity === 'P1') stats.p1 += Number(item.count);
      else if (item.severity === 'P2') stats.p2 += Number(item.count);
    });

    const members = memberAnalyses.map(a => {
      const issueStats = memberIssueMap.get(a.userId) || { p0: 0, p1: 0, p2: 0, total: 0 };
      const mustFixCount = issueStats.p0 + issueStats.p1;
      const suggestCount = issueStats.p2;
      const commitRatio = totalCommits > 0 ? (a.commitCount / totalCommits * 100).toFixed(1) : '0.0';
      const issueRatio = totalIssueCount > 0 ? (issueStats.total / totalIssueCount * 100).toFixed(1) : '0.0';

      // 质量评价逻辑
      let qualityRating = '优';
      if (issueStats.total === 0) {
        qualityRating = '优';
      } else if (mustFixCount >= 3 || issueStats.total >= 5) {
        qualityRating = '需重点关注';
      } else if (mustFixCount >= 1 || issueStats.total >= 3) {
        qualityRating = '待改进';
      } else {
        qualityRating = '良好';
      }

      return {
        id: a.userId,
        username: a.user.username,
        commitCount: a.commitCount,
        commitRatio: `${commitRatio}%`,
        insertions: a.insertions,
        deletions: a.deletions,
        netLines: a.insertions - a.deletions,
        mustFixCount,
        suggestCount,
        issueCount: issueStats.total,
        issueRatio: `${issueRatio}%`,
        qualityRating,
        fileChanges: a.fileChanges || [],
        aiQualityScore: a.aiQualityScore,
        aiQualityReport: a.aiQualityReport
      };
    });

    const avgScore = statistic?.avgQualityScore ? Number(statistic.avgQualityScore) : 
      (memberAnalyses.length > 0 ? 
        memberAnalyses.filter(a => a.aiQualityScore).reduce((sum, a) => sum + Number(a.aiQualityScore), 0) / 
        Math.max(memberAnalyses.filter(a => a.aiQualityScore).length, 1) : null);

    // 计算 AI 分析内容（使用已有的 totalCommits）
    const totalTasks = statistic?.totalTasks || memberAnalyses.reduce((sum, a) => sum + (a.taskCount || 0), 0);

    const report = {
      id: project.id,
      name: project.name,
      repository: project.repository,
      description: project.description,
      teamId: project.teamId,
      teamName: project.team?.name,
      techStack: project.techStack,
      isActive: project.isActive,
      defaultBranch: project.defaultBranch,
      lastCommitAt: project.lastCommitAt,
      periodType,
      periodValue,
      totalContributors: statistic?.totalContributors || memberAnalyses.length,
      totalCommits,
      totalInsertions: statistic?.totalInsertions || memberAnalyses.reduce((sum, a) => sum + a.insertions, 0),
      totalDeletions: statistic?.totalDeletions || memberAnalyses.reduce((sum, a) => sum + a.deletions, 0),
      totalTasks,
      totalLines: statistic?.totalLines || memberAnalyses.reduce((sum, a) => sum + a.totalLines, 0),
      avgQualityScore: avgScore,
      
      aiRating: statistic?.aiRating || (avgScore && avgScore >= 8 ? '优秀' : avgScore && avgScore >= 7 ? '良好' : '一般'),
      aiAdvantages: (statistic?.aiAdvantages as string[]) || [
        '项目代码结构清晰',
        `本周共完成 ${totalCommits} 次提交`,
        `${memberAnalyses.length} 位成员参与开发`
      ],
      aiSuggestions: (statistic?.aiSuggestions as string[]) || [
        '建议完善单元测试覆盖率',
        '持续优化代码结构',
        '加强代码审查流程'
      ],
      aiCommonIssues: (statistic?.aiCommonIssues as string[]) || [
        '部分代码缺少注释',
        '建议统一代码风格'
      ],
      aiBestPractices: (statistic?.aiBestPractices as string[]) || [
        '保持良好的提交习惯',
        '遵循团队代码规范'
      ],

      // 版本对比信息可以取最新的 analysis 记录，或者让上层传
      currentVersion: memberAnalyses[0]?.currentVersion || '',
      compareVersion: memberAnalyses[0]?.compareVersion || '',

      // 报告生成时间：使用最新分析记录的创建时间
      reportGeneratedAt: memberAnalyses[0]?.createdAt || statistic?.createdAt || new Date(),

      members
    };

    return {
      success: true,
      data: report,
    };
  }

  /**
   * 获取默认周期值
   */
  private getDefaultPeriodValue(periodType: 'week' | 'month' | 'quarter'): string {
    const now = new Date();
    if (periodType === 'week') {
      // 周维度：返回本周四的日期 (YYYYMMDD)
      const dayOfWeek = now.getDay();
      const daysToThursday = (4 - dayOfWeek + 7) % 7;
      const thursday = new Date(now);
      thursday.setDate(now.getDate() + daysToThursday);
      const year = thursday.getFullYear();
      const month = String(thursday.getMonth() + 1).padStart(2, '0');
      const day = String(thursday.getDate()).padStart(2, '0');
      return `${year}${month}${day}`;
    } else if (periodType === 'quarter') {
      // 季度维度：YYYY-Q1, YYYY-Q2, YYYY-Q3, YYYY-Q4
      const year = now.getFullYear();
      const month = now.getMonth();
      const quarter = Math.floor(month / 3) + 1;
      return `${year}-Q${quarter}`;
    } else {
      // 月维度：YYYYMM
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      return `${year}${month}`;
    }
  }
}