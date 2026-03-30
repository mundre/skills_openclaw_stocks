import { ApiProperty } from '@nestjs/swagger';
import { IsNotEmpty, IsString, IsOptional, IsArray } from 'class-validator';

export class TeamListItemDto {
  @ApiProperty({ description: '小组ID' })
  id: string;

  @ApiProperty({ description: '小组名称' })
  name: string;

  @ApiProperty({ description: '小组描述' })
  description: string | null;

  @ApiProperty({ description: '组长姓名' })
  leaderName: string | null;

  @ApiProperty({ description: '成员数量' })
  memberCount: number;

  @ApiProperty({ description: '项目数量' })
  projectCount: number;

  @ApiProperty({ description: '创建时间' })
  createdAt: Date;

  @ApiProperty({ description: '更新时间' })
  updatedAt: Date;
}

export class TeamMemberDto {
  @ApiProperty({ description: '用户ID' })
  id: string;

  @ApiProperty({ description: '用户名' })
  username: string;

  @ApiProperty({ description: '邮箱' })
  email: string;

  @ApiProperty({ description: '头像' })
  avatar: string | null;

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

export class TeamProjectDto {
  @ApiProperty({ description: '项目ID' })
  id: string;

  @ApiProperty({ description: '项目名称' })
  name: string;

  @ApiProperty({ description: '仓库地址' })
  repository: string;

  @ApiProperty({ description: '技术栈' })
  techStack: Record<string, any> | null;

  @ApiProperty({ description: '贡献者数量' })
  contributorCount: number;

  @ApiProperty({ description: '提交次数' })
  commitCount: number;

  @ApiProperty({ description: '代码行数' })
  codeLines: number;

  @ApiProperty({ description: 'AI质量评分' })
  aiQualityScore: number | null;
}

export class TeamReportDto {
  @ApiProperty({ description: '小组ID' })
  teamId: string;

  @ApiProperty({ description: '小组名称' })
  teamName: string;

  @ApiProperty({ description: '组长姓名' })
  leaderName: string;

  @ApiProperty({ description: '周期类型' })
  periodType: string;

  @ApiProperty({ description: '周期值' })
  periodValue: string;

  @ApiProperty({ description: '总成员数' })
  totalMembers: number;

  @ApiProperty({ description: '活跃成员数' })
  activeMembers: number;

  @ApiProperty({ description: '总提交数' })
  totalCommits: number;

  @ApiProperty({ description: '新增行数' })
  totalInsertions: number;

  @ApiProperty({ description: '删除行数' })
  totalDeletions: number;

  @ApiProperty({ description: '总任务数' })
  totalTasks: number;

  @ApiProperty({ description: '平均质量分' })
  avgQualityScore: number | null;

  @ApiProperty({ description: 'AI 分析摘要' })
  aiSummary: string;

  @ApiProperty({ description: 'AI 评级' })
  aiRating: string;

  @ApiProperty({ description: 'AI 优势分析' })
  aiAdvantages: string[];

  @ApiProperty({ description: 'AI 改进建议' })
  aiSuggestions: string[];

  @ApiProperty({ description: '报告生成时间' })
  reportGeneratedAt: Date;

  @ApiProperty({ description: '成员详情', type: [TeamMemberDto] })
  members: TeamMemberDto[];

  @ApiProperty({ description: '项目详情', type: [TeamProjectDto] })
  projects: TeamProjectDto[];
}

export class CreateTeamDto {
  @ApiProperty({ description: '小组名称', example: '运营前端组' })
  @IsNotEmpty({ message: '小组名称不能为空' })
  @IsString()
  name: string;

  @ApiProperty({ description: '小组描述', example: '负责运营相关前端项目开发', required: false })
  @IsOptional()
  @IsString()
  description?: string;

  @ApiProperty({ description: '组长姓名', example: '张三', required: false })
  @IsOptional()
  @IsString()
  leaderName?: string;

  @ApiProperty({ description: '成员名称列表', type: [String], required: false })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  memberNames?: string[];
}

export class UpdateTeamDto {
  @ApiProperty({ description: '小组名称', required: false })
  @IsOptional()
  @IsString()
  name?: string;

  @ApiProperty({ description: '小组描述', required: false })
  @IsOptional()
  @IsString()
  description?: string;

  @ApiProperty({ description: '组长姓名', required: false })
  @IsOptional()
  @IsString()
  leaderName?: string;

  @ApiProperty({ description: '成员名称列表', type: [String], required: false })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  memberNames?: string[];
}

export class TeamDetailDto extends TeamListItemDto {
  @ApiProperty({ description: '组长ID' })
  leaderId: string | null;

  @ApiProperty({ description: '成员列表' })
  members: TeamMemberSimpleDto[];
}

export class TeamMemberSimpleDto {
  @ApiProperty({ description: '用户ID' })
  id: string;

  @ApiProperty({ description: '用户名' })
  username: string;

  @ApiProperty({ description: '邮箱' })
  email: string;

  @ApiProperty({ description: '是否为组长' })
  isLeader: boolean;
}

export class CreateMemberDto {
  @ApiProperty({ description: '用户名', example: 'zhangsan' })
  @IsNotEmpty()
  @IsString()
  username: string;

  @ApiProperty({ description: '邮箱', example: 'zhangsan@example.com' })
  @IsNotEmpty()
  @IsString()
  email: string;

  @ApiProperty({ description: '是否为组长', default: false })
  @IsOptional()
  isLeader?: boolean;
}
