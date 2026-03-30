import { ApiProperty } from '@nestjs/swagger';
import { IsOptional, IsString, IsIn } from 'class-validator';

export class ProjectListQueryDto {
  @ApiProperty({ description: '页码', default: 1, required: false })
  page?: number = 1;

  @ApiProperty({ description: '每页数量', default: 10, required: false })
  limit?: number = 10;

  @ApiProperty({ description: '小组ID', required: false })
  teamId?: string;

  @ApiProperty({ description: '是否激活', required: false })
  isActive?: boolean;
}

export class ProjectReportQueryDto {
  @ApiProperty({
    description: '周期类型',
    enum: ['week', 'month', 'quarter'],
    default: 'week',
    required: false,
  })
  @IsOptional()
  @IsString()
  @IsIn(['week', 'month', 'quarter'])
  periodType?: 'week' | 'month' | 'quarter' = 'week';

  @ApiProperty({ description: '周期值', required: false })
  @IsOptional()
  @IsString()
  periodValue?: string;
}

export class ProjectListItemDto {
  @ApiProperty({ description: '项目ID' })
  id: string;

  @ApiProperty({ description: '项目名称' })
  name: string;

  @ApiProperty({ description: '仓库地址' })
  repository: string;

  @ApiProperty({ description: '项目描述', required: false })
  description?: string;

  @ApiProperty({ description: '小组ID', required: false })
  teamId?: string;

  @ApiProperty({ description: '小组名称', required: false })
  teamName?: string;

  @ApiProperty({ description: '技术栈', required: false })
  techStack?: any;

  @ApiProperty({ description: '是否激活' })
  isActive: boolean;

  @ApiProperty({ description: '默认分支', required: false })
  defaultBranch?: string;

  @ApiProperty({ description: '最后提交时间', required: false })
  lastCommitAt?: Date;

  @ApiProperty({ description: '创建时间' })
  createdAt: Date;

  @ApiProperty({ description: '更新时间' })
  updatedAt: Date;
}

export class ProjectReportDto {
  @ApiProperty({ description: '项目ID' })
  id: string;

  @ApiProperty({ description: '项目名称' })
  name: string;

  @ApiProperty({ description: '仓库地址' })
  repository: string;

  @ApiProperty({ description: '项目描述', required: false })
  description?: string;

  @ApiProperty({ description: '小组ID', required: false })
  teamId?: string;

  @ApiProperty({ description: '小组名称', required: false })
  teamName?: string;

  @ApiProperty({ description: '技术栈', required: false })
  techStack?: any;

  @ApiProperty({ description: '是否激活' })
  isActive: boolean;

  @ApiProperty({ description: '默认分支', required: false })
  defaultBranch?: string;

  @ApiProperty({ description: '最后提交时间', required: false })
  lastCommitAt?: Date;

  @ApiProperty({ description: '周期类型' })
  periodType: string;

  @ApiProperty({ description: '周期值' })
  periodValue: string;

  @ApiProperty({ description: '总贡献者数' })
  totalContributors: number;

  @ApiProperty({ description: '总提交数' })
  totalCommits: number;

  @ApiProperty({ description: '总新增行数' })
  totalInsertions: number;

  @ApiProperty({ description: '总删除行数' })
  totalDeletions: number;

  @ApiProperty({ description: '总任务数' })
  totalTasks: number;

  @ApiProperty({ description: '总代码行数' })
  totalLines: number;

  @ApiProperty({ description: '平均质量分数', required: false })
  avgQualityScore?: number;
}