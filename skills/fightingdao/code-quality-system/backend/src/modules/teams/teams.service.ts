import { Injectable, NotFoundException, ConflictException } from '@nestjs/common';
import { PrismaService } from '../../common/prisma.service';
import { 
  TeamListItemDto, 
  TeamDetailDto, 
  TeamMemberDto, 
  TeamProjectDto, 
  TeamReportDto,
  CreateTeamDto,
  UpdateTeamDto,
  TeamMemberSimpleDto
} from './dto/teams.dto';
import { PeriodQueryDto } from '../../common/dto/common.dto';
import { randomUUID } from 'crypto';

@Injectable()
export class TeamsService {
  constructor(private readonly prisma: PrismaService) {}

  /**
   * 获取小组列表
   */
  async getTeamList(): Promise<{ success: boolean; data: TeamListItemDto[] }> {
    const teams = await this.prisma.team.findMany({
      include: {
        users: {
          select: { id: true }
        },
        _count: {
          select: { projects: true }
        }
      },
      orderBy: {
        updatedAt: 'desc',
      },
    });

    const data: TeamListItemDto[] = teams.map((team) => ({
      id: team.id,
      name: team.name,
      description: team.description,
      leaderName: team.leaderName,
      memberCount: team.users.length,
      projectCount: team._count.projects,
      createdAt: team.createdAt,
      updatedAt: team.updatedAt,
    }));

    return {
      success: true,
      data,
    };
  }

  /**
   * 获取所有小组成员的用户名列表（用于Git提交匹配）
   */
  async getUserNames(): Promise<{ success: boolean; data: string[] }> {
    const users = await this.prisma.user.findMany({
      where: {
        teamId: { not: null }
      },
      select: {
        username: true,
      },
      orderBy: {
        username: 'asc',
      },
    });

    return {
      success: true,
      data: users.map(u => u.username),
    };
  }

  /**
   * 获取小组详情
   */
  async getTeamDetail(id: string): Promise<{ success: boolean; data: TeamDetailDto }> {
    return this.getTeamDetailWithTx(id, this.prisma);
  }

  /**
   * 创建小组
   */
  async createTeam(dto: CreateTeamDto): Promise<{ success: boolean; data: TeamDetailDto }> {
    const { name, description, leaderName, memberNames } = dto;
    
    // 检查小组名称是否已存在
    const existingTeam = await this.prisma.team.findFirst({
      where: { name }
    });
    
    if (existingTeam) {
      throw new ConflictException('小组名称已存在');
    }

    const teamId = `team-${randomUUID().slice(0, 8)}`;
    
    return this.prisma.$transaction(async (tx) => {
      // 1. 创建小组
      const team = await tx.team.create({
        data: {
          id: teamId,
          name: name,
          description: description || null,
          leaderName: leaderName || null,
        },
      });

      // 2. 处理成员同步
      if (memberNames && memberNames.length > 0) {
        for (const username of memberNames) {
          let user = await tx.user.findFirst({
            where: { username }
          });

          if (!user) {
            user = await tx.user.create({
              data: {
                id: `user-${randomUUID().slice(0, 8)}`,
                username: username,
                email: `${username}@internal.com`,
              }
            });
          }

          await tx.user.update({
            where: { id: user.id },
            data: { teamId: team.id }
          });
        }
      }

      return this.getTeamDetailWithTx(team.id, tx);
    });
  }

  /**
   * 更新小组
   */
  async updateTeam(teamId: string, dto: UpdateTeamDto): Promise<{ success: boolean; data: TeamDetailDto }> {
    const { name, description, leaderName, memberNames } = dto;
    
    const team = await this.prisma.team.findUnique({
      where: { id: teamId }
    });

    if (!team) {
      throw new NotFoundException('小组不存在');
    }

    if (name && name !== team.name) {
      const existingTeam = await this.prisma.team.findFirst({
        where: { name: name, id: { not: teamId } }
      });
      if (existingTeam) {
        throw new ConflictException('小组名称已存在');
      }
    }

    return this.prisma.$transaction(async (tx) => {
      await tx.team.update({
        where: { id: teamId },
        data: {
          name: name || undefined,
          description: description,
          leaderName: leaderName,
        },
      });

      if (memberNames !== undefined) {
        await tx.user.updateMany({
          where: { teamId },
          data: { teamId: null },
        });

        if (memberNames.length > 0) {
          for (const username of memberNames) {
            let user = await tx.user.findFirst({
              where: { username }
            });

            if (!user) {
              user = await tx.user.create({
                data: {
                  id: `user-${randomUUID().slice(0, 8)}`,
                  username: username,
                  email: `${username}@internal.com`,
                }
              });
            }

            await tx.user.update({
              where: { id: user.id },
              data: { teamId }
            });
          }
        }
      }

      return this.getTeamDetailWithTx(teamId, tx);
    });
  }

  /**
   * 获取详情的内部辅助方法（支持事务）
   */
  private async getTeamDetailWithTx(id: string, tx: any): Promise<{ success: boolean; data: TeamDetailDto }> {
    const team = await tx.team.findUnique({
      where: { id },
      include: {
        users: {
          select: {
            id: true,
            username: true,
            email: true,
          }
        },
        _count: {
          select: {
            projects: true
          }
        }
      }
    });

    if (!team) {
      throw new NotFoundException('小组不存在');
    }

    const data: TeamDetailDto = {
      id: team.id,
      name: team.name,
      description: team.description,
      leaderName: team.leaderName,
      memberCount: team.users.length,
      projectCount: team._count.projects,
      createdAt: team.createdAt,
      updatedAt: team.updatedAt,
      leaderId: null, // 由于模型中没有 isLeader，暂时设为 null 或根据业务逻辑调整
      members: team.users.map(u => ({
        id: u.id,
        username: u.username,
        email: u.email,
        isLeader: false,
      })),
    };

    return {
      success: true,
      data,
    };
  }

  /**
   * 删除小组
   */
  async deleteTeam(teamId: string): Promise<{ success: boolean; message: string }> {
    const team = await this.prisma.team.findUnique({
      where: { id: teamId }
    });

    if (!team) {
      throw new NotFoundException('小组不存在');
    }

    await this.prisma.user.updateMany({
      where: { teamId },
      data: { teamId: null },
    });

    await this.prisma.project.updateMany({
      where: { teamId },
      data: { teamId: null },
    });

    await this.prisma.teamStatistic.deleteMany({
      where: { teamId },
    });

    await this.prisma.team.delete({
      where: { id: teamId },
    });

    return {
      success: true,
      message: '小组删除成功',
    };
  }

  /**
   * 获取所有可用用户
   */
  async getAvailableUsers(): Promise<{ success: boolean; data: TeamMemberSimpleDto[] }> {
    const users = await this.prisma.user.findMany({
      where: {
        OR: [
          { teamId: null },
          { teamId: '' }
        ]
      },
      select: {
        id: true,
        username: true,
        email: true,
      },
      orderBy: {
        username: 'asc',
      },
    });

    return {
      success: true,
      data: users.map(u => ({
        id: u.id,
        username: u.username,
        email: u.email,
        isLeader: false,
      })),
    };
  }

  /**
   * 为小组添加成员
   */
  async addMember(teamId: string, username: string, email?: string, isLeader?: boolean): Promise<{ success: boolean; data: TeamMemberSimpleDto }> {
    const team = await this.prisma.team.findUnique({
      where: { id: teamId }
    });

    if (!team) {
      throw new NotFoundException('小组不存在');
    }

    // 检查用户是否已存在
    let user = await this.prisma.user.findFirst({
      where: { username }
    });

    if (!user) {
      // 创建新用户
      user = await this.prisma.user.create({
        data: {
          id: `user-${randomUUID().slice(0, 8)}`,
          username,
          email: email || `${username}@internal.com`,
          teamId,
        }
      });
    } else {
      // 更新用户的 teamId
      await this.prisma.user.update({
        where: { id: user.id },
        data: { teamId }
      });
    }

    // 如果是组长，更新小组的 leaderName
    if (isLeader) {
      await this.prisma.team.update({
        where: { id: teamId },
        data: { leaderName: username }
      });
    }

    return {
      success: true,
      data: {
        id: user.id,
        username: user.username,
        email: user.email,
        isLeader: isLeader || false,
      },
    };
  }

  /**
   * 从小组移除成员
   */
  async removeMember(teamId: string, userId: string): Promise<{ success: boolean; message: string }> {
    const user = await this.prisma.user.findUnique({
      where: { id: userId }
    });

    if (!user || user.teamId !== teamId) {
      throw new NotFoundException('该用户不在该小组中');
    }

    await this.prisma.user.update({
      where: { id: userId },
      data: { teamId: null }
    });

    return {
      success: true,
      message: '成员移除成功',
    };
  }

  /**
   * 获取小组报告
   */
  async getTeamReport(teamId: string, dto: PeriodQueryDto): Promise<{ success: boolean; data: TeamReportDto }> {
    const team = await this.prisma.team.findUnique({
      where: { id: teamId },
    });

    if (!team) {
      throw new NotFoundException('小组不存在');
    }

    const periodType = dto.periodType || 'week';
    const periodValue = dto.periodValue || this.getCurrentPeriodValue(periodType);

    const teamStatistic = await this.prisma.teamStatistic.findUnique({
      where: {
        teamId_periodType_periodValue: { teamId, periodType, periodValue },
      },
    });

    const users = await this.prisma.user.findMany({
      where: { teamId },
    });

    const userIds = users.map((u) => u.id);

    const memberAnalyses = await this.prisma.codeAnalysis.findMany({
      where: {
        userId: { in: userIds },
        periodType,
        periodValue,
      },
      include: {
        user: true,
        project: true,
      },
    });

    const memberMap = new Map<string, any>();
    for (const analysis of memberAnalyses) {
      const existing = memberMap.get(analysis.userId) || {
        id: analysis.userId,
        username: analysis.user.username,
        email: analysis.user.email,
        avatar: analysis.user.avatar,
        commitCount: 0,
        insertions: 0,
        deletions: 0,
        codeLines: 0,
        taskCount: 0,
        projects: [] as string[],
      };

      existing.commitCount += analysis.commitCount;
      existing.insertions += analysis.insertions;
      existing.deletions += analysis.deletions;
      existing.codeLines += analysis.codeLines;
      existing.taskCount += analysis.taskCount || 0;
      
      if (analysis.project && !existing.projects.includes(analysis.project.name)) {
        existing.projects.push(analysis.project.name);
      }

      memberMap.set(analysis.userId, existing);
    }

    const members: TeamMemberDto[] = Array.from(memberMap.values()).map((member) => {
      const memberScores = memberAnalyses
        .filter((a) => a.userId === member.id && a.aiQualityScore)
        .map((a) => Number(a.aiQualityScore));

      return {
        id: member.id,
        username: member.username,
        email: member.email,
        avatar: member.avatar,
        commitCount: member.commitCount,
        insertions: member.insertions,
        deletions: member.deletions,
        codeLines: member.codeLines,
        aiQualityScore: this.calculateAverageScore(memberScores),
        taskCount: member.taskCount,
        projects: member.projects.join(', ') || '-',
      } as any;
    });

    const teamProjects = await this.prisma.project.findMany({
      where: { teamId },
    });

    const projectIds = teamProjects.map((p) => p.id);

    const projectStatistics = await this.prisma.projectStatistic.findMany({
      where: {
        projectId: { in: projectIds },
        periodType,
        periodValue,
      },
    });

    // 从 code_analyses 聚合项目数据（当 project_statistics 没有数据时）
    const projectAnalysesMap = new Map<string, any>();
    for (const analysis of memberAnalyses) {
      if (analysis.project) {
        const existing = projectAnalysesMap.get(analysis.project.id) || {
          id: analysis.project.id,
          name: analysis.project.name,
          repository: analysis.project.repository,
          techStack: null,
          contributorCount: 0,
          commitCount: 0,
          insertions: 0,
          deletions: 0,
          codeLines: 0,
          aiQualityScore: null,
          scoreSum: 0,
          scoreCount: 0,
        };
        existing.contributorCount += 1;
        existing.commitCount += analysis.commitCount;
        existing.insertions += analysis.insertions;
        existing.deletions += analysis.deletions;
        existing.codeLines += analysis.codeLines;
        if (analysis.aiQualityScore) {
          existing.scoreSum += Number(analysis.aiQualityScore);
          existing.scoreCount += 1;
        }
        projectAnalysesMap.set(analysis.project.id, existing);
      }
    }

    // 合并团队项目和从分析数据中获取的项目
    const allProjectIds = new Set([...projectIds, ...Array.from(projectAnalysesMap.keys())]);
    const projects: any[] = [];

    for (const projectId of allProjectIds) {
      const teamProject = teamProjects.find((p) => p.id === projectId);
      const stat = projectStatistics.find((s) => s.projectId === projectId);
      const fromAnalyses = projectAnalysesMap.get(projectId);

      if (stat) {
        // 有 project_statistics 数据
        projects.push({
          id: projectId,
          name: teamProject?.name || fromAnalyses?.name || 'Unknown',
          repository: teamProject?.repository || fromAnalyses?.repository,
          techStack: teamProject?.techStack as Record<string, any> | null || null,
          contributorCount: stat.totalContributors || 0,
          commitCount: stat.totalCommits || 0,
          insertions: stat.totalInsertions || 0,
          deletions: stat.totalDeletions || 0,
          codeLines: stat.totalLines || 0,
          aiQualityScore: stat.avgQualityScore ? Number(stat.avgQualityScore) : null,
        });
      } else if (fromAnalyses) {
        // 从 code_analyses 聚合
        projects.push({
          id: fromAnalyses.id,
          name: fromAnalyses.name,
          repository: fromAnalyses.repository,
          techStack: fromAnalyses.techStack,
          contributorCount: fromAnalyses.contributorCount,
          commitCount: fromAnalyses.commitCount,
          insertions: fromAnalyses.insertions,
          deletions: fromAnalyses.deletions,
          codeLines: fromAnalyses.codeLines,
          aiQualityScore: fromAnalyses.scoreCount > 0 ? fromAnalyses.scoreSum / fromAnalyses.scoreCount : null,
        });
      } else if (teamProject) {
        // 团队项目但没有数据
        projects.push({
          id: teamProject.id,
          name: teamProject.name,
          repository: teamProject.repository,
          techStack: teamProject.techStack as Record<string, any> | null,
          contributorCount: 0,
          commitCount: 0,
          insertions: 0,
          deletions: 0,
          codeLines: 0,
          aiQualityScore: null,
        });
      }
    }

    // 计算 AI 分析内容
    const totalCommits = teamStatistic?.totalCommits || memberAnalyses.reduce((sum, a) => sum + a.commitCount, 0);
    const totalTasks = teamStatistic?.totalTasks || memberAnalyses.reduce((sum, a) => sum + (a.taskCount || 0), 0);
    const avgScore = teamStatistic?.avgQualityScore ? Number(teamStatistic.avgQualityScore) : 
      (memberAnalyses.length > 0 ? 
        memberAnalyses.filter(a => a.aiQualityScore).reduce((sum, a) => sum + Number(a.aiQualityScore), 0) / 
        memberAnalyses.filter(a => a.aiQualityScore).length : null);

    // 检查是否有数据
    const hasData = !!teamStatistic || memberAnalyses.length > 0;

    const report: any = {
      teamId: team.id,
      teamName: team.name,
      leaderName: team.leaderName || '未设置',
      periodType,
      periodValue,
      totalMembers: teamStatistic?.totalMembers || users.length,
      activeMembers: teamStatistic?.activeMembers || members.length,
      totalCommits,
      totalInsertions: teamStatistic?.totalInsertions || memberAnalyses.reduce((sum, a) => sum + a.insertions, 0),
      totalDeletions: teamStatistic?.totalDeletions || memberAnalyses.reduce((sum, a) => sum + a.deletions, 0),
      totalTasks,
      avgQualityScore: avgScore,
      // AI 分析内容 - 没有数据时返回空
      aiSummary: hasData ? (teamStatistic?.aiSummary || 
        `本周${team.name}共完成 ${totalCommits} 次提交，涉及 ${totalTasks} 个需求任务。代码质量${avgScore && avgScore >= 7 ? '良好' : '一般'}，平均得分 ${avgScore?.toFixed(1) || '-'} 分。`) : '本周暂无代码提交数据',
      aiRating: hasData ? (teamStatistic?.aiRating || (avgScore && avgScore >= 8 ? '优秀' : avgScore && avgScore >= 7 ? '良好' : '一般')) : '-',
      aiAdvantages: hasData ? ((teamStatistic?.aiAdvantages as string[]) || ['团队整体代码质量良好', '任务完成效率高']) : [],
      aiSuggestions: hasData ? ((teamStatistic?.aiSuggestions as string[]) || ['建议完善单元测试覆盖率', '持续优化代码结构']) : [],
      reportGeneratedAt: teamStatistic?.createdAt || new Date(),
      members,
      // 过滤掉没有提交的项目
      projects: projects.filter(p => p.commitCount > 0),
    };

    return {
      success: true,
      data: report,
    };
  }

  private getCurrentPeriodValue(periodType: 'week' | 'month' | 'quarter'): string {
    const now = new Date();
    if (periodType === 'month') {
      return `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}`;
    } else if (periodType === 'quarter') {
      return `${now.getFullYear()}Q${Math.floor(now.getMonth() / 3) + 1}`;
    } else {
      const d = new Date(now);
      d.setDate(d.getDate() + ((4 - d.getDay() + 7) % 7));
      return `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`;
    }
  }

  private calculateAverageScore(scores: number[]): number | null {
    if (scores.length === 0) return null;
    const sum = scores.reduce((acc, score) => acc + score, 0);
    return Math.round((sum / scores.length) * 100) / 100;
  }
}
