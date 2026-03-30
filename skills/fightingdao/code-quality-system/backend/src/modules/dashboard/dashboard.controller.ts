import { Controller, Get, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { DashboardService } from './dashboard.service';
import { PeriodQueryDto } from '../../common/dto/common.dto';

@ApiTags('大盘视图')
@Controller('api/v1/dashboard')
export class DashboardController {
  constructor(private readonly dashboardService: DashboardService) {}

  @Get('overview')
  @ApiOperation({ summary: '获取大盘统计数据' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getOverview(@Query() dto: PeriodQueryDto) {
    return this.dashboardService.getOverview(dto);
  }

  @Get('teams')
  @ApiOperation({ summary: '获取各小组整体分析报告' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getTeamDashboards(@Query() dto: PeriodQueryDto) {
    return this.dashboardService.getTeamDashboards(dto);
  }

  @Get('analyses')
  @ApiOperation({ summary: '获取代码分析列表（支持筛选和排序）' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getCodeAnalysisList(
    @Query() dto: PeriodQueryDto & {
      page?: number;
      limit?: number;
      teamId?: string;
      projectId?: string;
      userName?: string;
      version?: string;
      sortBy?: string;
      sortOrder?: 'asc' | 'desc';
    }
  ) {
    return this.dashboardService.getCodeAnalysisList(dto);
  }

  @Get('project-analyses')
  @ApiOperation({ summary: '获取项目维度分析列表（用于项目概览）' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getProjectAnalysisList(
    @Query() dto: PeriodQueryDto & {
      page?: number;
      limit?: number;
      projectId?: string;
      version?: string;
      userName?: string;
    }
  ) {
    return this.dashboardService.getProjectAnalysisList(dto);
  }

  @Get('filter-options')
  @ApiOperation({ summary: '获取筛选选项数据' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getFilterOptions(@Query() dto: PeriodQueryDto) {
    return this.dashboardService.getFilterOptions(dto);
  }
}