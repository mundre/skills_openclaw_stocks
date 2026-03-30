import { ApiProperty } from '@nestjs/swagger';

export class UserAnalysisQueryDto {
  @ApiProperty({
    description: '周期类型',
    enum: ['week', 'month', 'quarter'],
    default: 'week',
    required: false,
  })
  periodType?: 'week' | 'month' | 'quarter' = 'week';

  @ApiProperty({ description: '周期值', required: false })
  periodValue?: string;

  @ApiProperty({ description: '项目ID（可选，不传则返回所有项目的汇总）', required: false })
  projectId?: string;

  @ApiProperty({ description: '页码', default: 1, required: false })
  page?: number = 1;

  @ApiProperty({ description: '每页数量', default: 10, required: false })
  limit?: number = 10;
}

export class UserBasicInfoDto {
  @ApiProperty({ description: '用户ID' })
  id: string;

  @ApiProperty({ description: '用户名' })
  username: string;

  @ApiProperty({ description: '邮箱' })
  email: string;

  @ApiProperty({ description: '头像', required: false })
  avatar?: string;

  @ApiProperty({ description: '小组ID', required: false })
  teamId?: string;

  @ApiProperty({ description: '小组名称', required: false })
  teamName?: string;

  @ApiProperty({ description: 'Git用户名', required: false })
  gitUsername?: string;

  @ApiProperty({ description: 'Git邮箱', required: false })
  gitEmail?: string;
}

export class UserStatisticsDto {
  @ApiProperty({ description: '总提交次数' })
  totalCommits: number;

  @ApiProperty({ description: '总新增行数' })
  totalInsertions: number;

  @ApiProperty({ description: '总删除行数' })
  totalDeletions: number;

  @ApiProperty({ description: '总代码行数' })
  totalCodeLines: number;

  @ApiProperty({ description: '总任务数' })
  totalTasks: number;

  @ApiProperty({ description: '平均质量分', nullable: true })
  avgQualityScore: number | null;
}

export class CodeAnalysisItemDto {
  @ApiProperty({ description: '分析ID' })
  id: string;

  @ApiProperty({ description: '项目ID' })
  projectId: string;

  @ApiProperty({ description: '项目名称' })
  projectName: string;

  @ApiProperty({ description: '周期类型' })
  periodType: string;

  @ApiProperty({ description: '周期值' })
  periodValue: string;

  @ApiProperty({ description: '提交次数' })
  commitCount: number;

  @ApiProperty({ description: '新增行数' })
  insertions: number;

  @ApiProperty({ description: '删除行数' })
  deletions: number;

  @ApiProperty({ description: '代码行数' })
  codeLines: number;

  @ApiProperty({ description: 'AI质量评分', nullable: true })
  aiQualityScore: number | null;

  @ApiProperty({ description: '任务数量' })
  taskCount: number;

  @ApiProperty({ description: '创建时间' })
  createdAt: Date;
}

export class UserAnalysisDto {
  @ApiProperty({ description: '用户基本信息' })
  user: UserBasicInfoDto;

  @ApiProperty({ description: '统计数据（指定周期内）' })
  statistics: UserStatisticsDto;

  @ApiProperty({ description: '代码分析记录列表' })
  analyses: CodeAnalysisItemDto[];

  @ApiProperty({ description: '分页信息' })
  meta: {
    total: number;
    page: number;
    limit: number;
    hasMore: boolean;
  };
}