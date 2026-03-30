import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('开始填充测试数据...');

  // 清空现有数据
  await prisma.codeReview.deleteMany();
  await prisma.codeAnalysis.deleteMany();
  await prisma.teamStatistic.deleteMany();
  await prisma.projectStatistic.deleteMany();
  await prisma.user.deleteMany();
  await prisma.project.deleteMany();
  await prisma.team.deleteMany();

  // 1. 创建小组
  const team1 = await prisma.team.create({
    data: {
      id: 'team-001',
      name: '商业化开发组',
      leaderName: '汤曙磊',
      description: '负责商业化核心业务开发',
    },
  });

  const team2 = await prisma.team.create({
    data: {
      id: 'team-002',
      name: '流量运营开发组',
      leaderName: '桂清清',
      description: '负责流量分发与运营工具',
    },
  });

  const team3 = await prisma.team.create({
    data: {
      id: 'team-003',
      name: '运营平台开发组',
      leaderName: '周学成',
      description: '负责中台运营系统',
    },
  });

  // 2. 创建用户
  const users = await Promise.all([
    prisma.user.create({ data: { id: 'u1', username: 'houfeng-jk', email: 'hf@test.com', teamId: team2.id } }),
    prisma.user.create({ data: { id: 'u2', username: 'zhangwenhan-jwk', email: 'zwh@test.com', teamId: team3.id } }),
    prisma.user.create({ data: { id: 'u3', username: 'wangwu-jk', email: 'ww@test.com', teamId: team2.id } }),
    prisma.user.create({ data: { id: 'u4', username: 'zhaojiannan-jk', email: 'zjn@test.com', teamId: team1.id } }),
  ]);

  // 3. 创建项目
  const p1 = await prisma.project.create({ data: { id: 'p1', name: 'tmk-web', repository: 'git/tmk-web', teamId: team1.id, defaultBranch: 'develop' } });
  const p2 = await prisma.project.create({ data: { id: 'p2', name: 'dove_digital', repository: 'git/dove', teamId: team2.id, defaultBranch: 'feature/sfe2.66.0' } });
  const p3 = await prisma.project.create({ data: { id: 'p3', name: 'intelget-voice-anlys-web', repository: 'git/voice', teamId: team3.id, defaultBranch: 'master' } });

  // 4. 创建代码分析数据 (20260312 - 周四)
  const periodType = 'week';
  const periodValue = '20260312';

  await prisma.codeAnalysis.createMany({
    data: [
      {
        id: 'a1', userId: 'u1', projectId: 'p2', periodType, periodValue,
        branch: 'feature/sfe2.66.0', currentVersion: 'origin/featsfe2.66.0-20260305', compareVersion: 'iopsfe2.64.0-20260205',
        commitCount: 28, insertions: 2439, deletions: 862, filesChanged: 15,
        totalLines: 5000, codeLines: 4000, commentLines: 500, blankLines: 500,
        aiQualityScore: 88, aiQualityReport: '整体代码质量良好', taskCount: 12
      },
      {
        id: 'a2', userId: 'u2', projectId: 'p3', periodType, periodValue,
        branch: 'master', currentVersion: 'origin/20260305', compareVersion: '20260122',
        commitCount: 25, insertions: 1280, deletions: 320, filesChanged: 8,
        totalLines: 3000, codeLines: 2500, commentLines: 300, blankLines: 200,
        aiQualityScore: 85, taskCount: 8
      },
      {
        id: 'a3', userId: 'u4', projectId: 'p1', periodType, periodValue,
        branch: 'develop', currentVersion: 'origin/20260305', compareVersion: '20260122',
        commitCount: 20, insertions: 3555, deletions: 455, filesChanged: 20,
        totalLines: 8000, codeLines: 7000, commentLines: 600, blankLines: 400,
        aiQualityScore: 92, taskCount: 15
      }
    ]
  });

  // 5. 创建代码评审记录 (CodeReview)
  await prisma.codeReview.createMany({
    data: [
      {
        id: 'r1', analysisId: 'a1', commitHash: '95ff935d', commitMessage: 'feat(YSG-140427): 优化流程限制时间设置',
        commitBranch: 'feature/sfe2.66.0', commitDate: new Date('2026-03-05 11:22:18'),
        committerId: 'u1', committerName: 'houfeng-jk', status: 'approved'
      },
      {
        id: 'r2', analysisId: 'a1', commitHash: '6bde0c27', commitMessage: 'feat(PD-40626): 增加筛选条件校验逻辑',
        commitBranch: 'feature/sfe2.66.0', commitDate: new Date('2026-03-04 08:20:45'),
        committerId: 'u1', committerName: 'houfeng-jk', status: 'approved'
      }
    ]
  });

  // 6. 创建小组统计 (TeamStatistic)
  await prisma.teamStatistic.create({
    data: {
      teamId: team1.id, periodType, periodValue,
      totalMembers: 3, activeMembers: 3, totalCommits: 75, totalInsertions: 5000, totalDeletions: 1000, totalTasks: 16,
      avgQualityScore: 87, aiRating: '优秀',
      aiSummary: '本周商业化组表现出色，代码提交频率高且质量稳定。',
      aiAdvantages: ['核心逻辑清晰', '覆盖了关键业务场景'],
      aiSuggestions: ['建议加强对旧逻辑的重构']
    }
  });

  // 7. 创建项目统计 (ProjectStatistic)
  await prisma.projectStatistic.create({
    data: {
      projectId: p1.id, periodType, periodValue,
      totalContributors: 3, totalCommits: 48, totalInsertions: 5420, totalDeletions: 1680, totalTasks: 10, totalLines: 15000,
      avgQualityScore: 89, aiRating: '卓越',
      aiAdvantages: ['架构设计合理', '性能优化显著'],
      aiCommonIssues: ['个别方法圈复杂度过高'],
      aiBestPractices: ['统一了错误处理机制']
    }
  });

  console.log('✅ Mock数据填充完成！');
}

main()
  .catch((e) => {
    console.error('填充数据失败:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
