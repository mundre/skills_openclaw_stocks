import { Controller, Get, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { ProjectsService } from './projects.service';
import {
  ProjectListQueryDto,
  ProjectReportQueryDto,
} from './dto/projects.dto';

@ApiTags('项目管理')
@Controller('api/v1/projects')
export class ProjectsController {
  constructor(private readonly projectsService: ProjectsService) {}

  @Get()
  @ApiOperation({ summary: '获取项目列表' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getProjectList(@Query() dto: ProjectListQueryDto) {
    return this.projectsService.getProjectList(dto);
  }

  @Get(':id')
  @ApiOperation({ summary: '获取项目信息' })
  @ApiResponse({ status: 200, description: '获取成功' })
  @ApiResponse({ status: 404, description: '项目不存在' })
  async getProjectInfo(@Param('id') id: string) {
    return this.projectsService.getProjectInfo(id);
  }

  @Get(':id/report')
  @ApiOperation({ summary: '获取项目报告' })
  @ApiResponse({ status: 200, description: '获取成功' })
  @ApiResponse({ status: 404, description: '项目不存在' })
  async getProjectReport(
    @Param('id') id: string,
    @Query() dto: ProjectReportQueryDto,
  ) {
    return this.projectsService.getProjectReport(id, dto);
  }
}