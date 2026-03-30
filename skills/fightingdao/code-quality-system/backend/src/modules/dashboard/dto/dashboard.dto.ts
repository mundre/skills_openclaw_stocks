import { ApiProperty } from '@nestjs/swagger';

export class DashboardOverviewDto {
  @ApiProperty({ description: '总成员数' })
  totalMembers: number;

  @ApiProperty({ description: '总提交数' })
  totalCommits: number;

  @ApiProperty({ description: '总任务数' })
  totalTasks: number;

  @ApiProperty({ description: '平均质量分' })
  avgQualityScore: number | null;
}

export class TeamDashboardDto {
  @ApiProperty({ description: '小组ID' })
  id: string;

  @ApiProperty({ description: '小组名称' })
  name: string;

  @ApiProperty({ description: '总成员数' })
  totalMembers: number;

  @ApiProperty({ description: '活跃成员数' })
  activeMembers: number;

  @ApiProperty({ description: '总提交数' })
  totalCommits: number;

  @ApiProperty({ description: '新增行数' })
  insertions: number;

  @ApiProperty({ description: '删除行数' })
  deletions: number;

  @ApiProperty({ description: '平均质量分' })
  avgQualityScore: number | null;
}

export class CodeAnalysisListItemDto {
  @ApiProperty({ description: '分析ID' })
  id: string;

  @ApiProperty({ description: '用户名' })
  userName: string;

  @ApiProperty({ description: '项目名称' })
  projectName: string;

  @ApiProperty({ description: '提交次数' })
  commitCount: number;

  @ApiProperty({ description: '新增行数' })
  insertions: number;

  @ApiProperty({ description: '删除行数' })
  deletions: number;

  @ApiProperty({ description: '代码行数' })
  codeLines: number;

  @ApiProperty({ description: 'AI质量评分' })
  aiQualityScore: number | null;

  @ApiProperty({ description: '任务数量' })
  taskCount: number;
}