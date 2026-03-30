import { Injectable, NotFoundException } from '@nestjs/common';
import { PrismaService } from '../../common/prisma.service';
import { UserAnalysisQueryDto } from './dto/users.dto';

@Injectable()
export class UsersService {
  constructor(private prisma: PrismaService) {}

  /**
   * 获取用户分析数据
   * 支持按项目过滤：如果传入 projectId，返回该用户在指定项目、指定周期的详情
   * 如果不传 projectId，返回该用户在指定周期的所有项目汇总
   */
  async getUserAnalysis(userId: string, dto: UserAnalysisQueryDto) {
    // 查询用户基本信息
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      include: {
        team: true,
      },
    });

    if (!user) {
      throw new NotFoundException(`用户 ${userId} 不存在`);
    }

    // 构建查询条件
    const where: any = { userId };
    if (dto.periodType) {
      where.periodType = dto.periodType;
    }
    if (dto.periodValue) {
      where.periodValue = dto.periodValue;
    }
    // 支持按项目过滤
    if (dto.projectId) {
      where.projectId = dto.projectId;
    }

    // 分页参数
    const page = dto.page || 1;
    const limit = dto.limit || 10;
    const skip = (page - 1) * limit;

    // 并行查询统计数据、分析记录和具体的评审记录
    const [analyses, total, statsResult, reviews] = await Promise.all([
      this.prisma.codeAnalysis.findMany({
        where,
        skip,
        take: limit,
        include: {
          project: {
            include: { team: true }
          },
        },
        orderBy: {
          createdAt: 'desc',
        },
      }),
      this.prisma.codeAnalysis.count({ where }),
      this.prisma.codeAnalysis.aggregate({
        where,
        _sum: {
          commitCount: true,
          insertions: true,
          deletions: true,
          codeLines: true,
          taskCount: true,
        },
        _avg: {
          aiQualityScore: true,
        },
      }),
      // 查询评审记录：如果指定了项目，只查该项目的评审记录
      this.prisma.codeReview.findMany({
        where: {
          committerId: userId,
          analysis: {
            periodType: dto.periodType,
            periodValue: dto.periodValue,
            ...(dto.projectId ? { projectId: dto.projectId } : {})
          }
        },
        include: {
          analysis: {
            include: { project: true }
          }
        },
        orderBy: { commitDate: 'desc' }
      })
    ]);

    // 获取用户参与的所有项目列表（该周期内）
    const projectAnalyses = await this.prisma.codeAnalysis.findMany({
      where: {
        userId,
        periodType: dto.periodType,
        periodValue: dto.periodValue
      },
      include: {
        project: true
      }
    });
    
    const projects = projectAnalyses.map(a => ({
      id: a.projectId,
      name: a.project.name,
      commitCount: a.commitCount,
      insertions: a.insertions,
      deletions: a.deletions,
      aiQualityScore: a.aiQualityScore ? Number(a.aiQualityScore) : null
    }));

    // 构建用户基本信息
    const userBasicInfo = {
      id: user.id,
      username: user.username,
      email: user.email,
      avatar: user.avatar,
      teamId: user.teamId,
      teamName: user.team?.name,
      gitUsername: user.gitUsername,
      gitEmail: user.gitEmail,
      reportTime: analyses[0]?.createdAt || new Date(),
    };

    // 构建统计数据
    const statistics = {
      totalCommits: statsResult._sum.commitCount || 0,
      totalInsertions: statsResult._sum.insertions || 0,
      totalDeletions: statsResult._sum.deletions || 0,
      netGrowth: (statsResult._sum.insertions || 0) - (statsResult._sum.deletions || 0),
      totalCodeLines: statsResult._sum.codeLines || 0,
      totalTasks: statsResult._sum.taskCount || 0,
      avgQualityScore: statsResult._avg.aiQualityScore
        ? Math.round((statsResult._avg.aiQualityScore as any) * 100) / 100
        : null,
    };

    // 构建详细的分析数据（取最近的一条分析作为报告主体）
    const latestAnalysis = analyses[0];
    
    // 从 aiQualityReport 解析 AI 报告内容
    let issues: string[] = [];
    let suggestions: string[] = [];
    let advantages: string[] = [];
    let overallEvaluation = '良好';
    
    if (latestAnalysis?.aiQualityReport) {
      const reportContent = latestAnalysis.aiQualityReport;
      
      // 解析问题列表
      const issuesMatch = reportContent.match(/### 主要问题\n([\s\S]*?)(?=\n###|$)/);
      if (issuesMatch) {
        const content = issuesMatch[1].trim();
        // 先尝试匹配带数字前缀的行
        const numberedLines = content.split('\n')
          .filter((line: string) => line.trim().match(/^\d+\./))
          .map((line: string) => line.replace(/^\d+\.\s*/, '').trim());
        
        if (numberedLines.length > 0) {
          issues = numberedLines;
        } else if (content && !content.includes('暂无')) {
          // 如果没有数字前缀但也不是"暂无"，直接作为单条内容
          issues = [content];
        }
      }
      
      // 解析建议列表
      const suggestionsMatch = reportContent.match(/### 改进建议\n([\s\S]*?)(?=\n###|$)/);
      if (suggestionsMatch) {
        const content = suggestionsMatch[1].trim();
        const numberedLines = content.split('\n')
          .filter((line: string) => line.trim().match(/^\d+\./))
          .map((line: string) => line.replace(/^\d+\.\s*/, '').trim());
        
        if (numberedLines.length > 0) {
          suggestions = numberedLines;
        } else if (content && !content.includes('暂无')) {
          suggestions = [content];
        }
      }
      
      // 解析亮点列表
      const advantagesMatch = reportContent.match(/### 亮点\n([\s\S]*?)(?=\n###|$)/);
      if (advantagesMatch) {
        const content = advantagesMatch[1].trim();
        const numberedLines = content.split('\n')
          .filter((line: string) => line.trim().match(/^\d+\./))
          .map((line: string) => line.replace(/^\d+\.\s*/, '').trim());
        
        if (numberedLines.length > 0) {
          advantages = numberedLines;
        } else if (content && !content.includes('暂无')) {
          advantages = [content];
        }
      }
      
      // 解析总体评价
      const ratingMatch = reportContent.match(/### 总体评价：(.+)/);
      if (ratingMatch) {
        overallEvaluation = ratingMatch[1].trim();
      }
    }
    
    // 从 languages JSON 中提取提交类型统计
    let commitTypes: Record<string, number> = {};
    let fileChanges: Array<{ path: string; insertions: number; deletions: number; type: string }> = [];
    
    if (latestAnalysis?.languages) {
      const langData = latestAnalysis.languages as any;
      if (langData.commitTypes) {
        commitTypes = langData.commitTypes;
      }
    }
    
    // 如果没有 commitTypes，从 commits 数据计算
    if (Object.keys(commitTypes).length === 0 && reviews.length > 0) {
      for (const r of reviews) {
        let commitType = '其他';
        if (r.reviewResult) {
          try {
            const result = JSON.parse(r.reviewResult as string);
            const typeMap: Record<string, string> = {
              'feat': '新功能',
              'fix': 'Bug修复',
              'refactor': '重构',
              'style': '样式',
              'test': '测试',
              'docs': '文档',
              'chore': '杂项',
              'perf': '性能优化',
              '新功能': '新功能',
              'Bug修复': 'Bug修复',
              '重构': '重构',
              '样式': '样式',
              '测试': '测试',
              '文档': '文档',
              '杂项': '杂项',
              '性能优化': '性能优化',
              '其他': '其他',
              'other': '其他'
            };
            commitType = typeMap[result.type] || result.type || '其他';
          } catch (e) {}
        }
        // 备用：从 commit message 判断
        if (commitType === '其他' && r.commitMessage) {
          if (r.commitMessage.startsWith('feat')) commitType = '新功能';
          else if (r.commitMessage.startsWith('fix')) commitType = 'Bug修复';
          else if (r.commitMessage.startsWith('refactor')) commitType = '重构';
          else if (r.commitMessage.startsWith('style')) commitType = '样式';
          else if (r.commitMessage.startsWith('test')) commitType = '测试';
          else if (r.commitMessage.startsWith('docs')) commitType = '文档';
          else if (r.commitMessage.startsWith('chore')) commitType = '杂项';
          else if (r.commitMessage.startsWith('perf')) commitType = '性能优化';
        }
        commitTypes[commitType] = (commitTypes[commitType] || 0) + 1;
      }
    }
    
    if (latestAnalysis?.fileChanges) {
      fileChanges = latestAnalysis.fileChanges as any[];
    }
    
    const report = {
      projectId: latestAnalysis?.projectId || null,
      projectName: latestAnalysis?.project?.name || null,
      branch: latestAnalysis?.branch || '',
      currentVersion: latestAnalysis?.currentVersion || '',
      compareVersion: latestAnalysis?.compareVersion || '',
      commitCount: latestAnalysis?.commitCount || 0,
      issues,
      suggestions,
      advantages,
      overallEvaluation,
      commitTypes,
      fileChanges
    };

    return {
      success: true,
      data: {
        user: userBasicInfo,
        statistics,
        report,
        projects,  // 用户在该周期参与的所有项目
        commits: reviews.map(r => {
          // 从 reviewResult JSON 中解析提交详情
          let insertions = 0;
          let deletions = 0;
          let commitType = '其他';
          
          if (r.reviewResult) {
            try {
              const result = JSON.parse(r.reviewResult);
              insertions = result.insertions || 0;
              deletions = result.deletions || 0;
              // 数据库存的是英文类型，需要映射为中文
              const typeMap: Record<string, string> = {
                'feat': '新功能',
                'fix': 'Bug修复',
                'refactor': '重构',
                'style': '样式',
                'test': '测试',
                'docs': '文档',
                'chore': '杂项',
                'perf': '性能优化',
                'other': '其他'
              };
              commitType = typeMap[result.type] || result.type || '其他';
            } catch (e) {
              // 解析失败使用默认值
            }
          }
          
          // 根据 commit message 判断类型（备用方案）
          if (commitType === '其他' && r.commitMessage) {
            if (r.commitMessage.startsWith('feat')) commitType = '新功能';
            else if (r.commitMessage.startsWith('fix')) commitType = 'Bug修复';
            else if (r.commitMessage.startsWith('refactor')) commitType = '重构';
          }
          
          return {
            hash: r.commitHash.substring(0, 7),
            message: r.commitMessage,
            type: commitType,
            time: r.commitDate ? new Date(r.commitDate).toISOString() : null,
            insertions,
            deletions,
            projectName: r.analysis?.project?.name || null
          };
        }),
        meta: {
          total,
          page,
          limit,
          hasMore: total > page * limit,
        },
      },
    };
  }
}