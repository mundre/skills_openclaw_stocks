import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { CodeReviewService } from './code-review.service';

@Controller('api/v1/code-review')
export class CodeReviewController {
  constructor(
    private readonly codeReviewService: CodeReviewService,
  ) {}

  /**
   * 获取项目的代码审查问题
   * projectId 可以是 UUID 或项目名称
   */
  @Get(':projectId')
  async getProjectIssues(
    @Param('projectId') projectId: string,
    @Query('periodType') periodType: string,
    @Query('periodValue') periodValue: string
  ) {
    // 如果不是 UUID，尝试按名称查找
    const actualProjectId = await this.codeReviewService.resolveProjectId(projectId);
    if (!actualProjectId) {
      return {
        success: false,
        error: `项目不存在: ${projectId}`
      };
    }

    const issues = await this.codeReviewService.getProjectIssues(actualProjectId, periodType, periodValue);
    const summary = await this.codeReviewService.getProjectReviewSummary(actualProjectId, periodType, periodValue);
    
    return {
      success: true,
      data: {
        issues,
        summary
      }
    };
  }

  /**
   * 保存代码审查报告
   */
  @Post(':projectId')
  async saveReviewReport(
    @Param('projectId') projectId: string,
    @Query('periodType') periodType: string,
    @Query('periodValue') periodValue: string,
    @Body() report: {
      overview: any;
      issues: any[];
      commonIssues: any[];
      highlights: any[];
      priority: any[];
    }
  ) {
    const result = await this.codeReviewService.saveReviewReport(projectId, periodType, periodValue, report);
    return result;
  }

  /**
   * 获取项目代码审查汇总
   */
  @Get(':projectId/summary')
  async getSummary(
    @Param('projectId') projectId: string,
    @Query('periodType') periodType: string,
    @Query('periodValue') periodValue: string
  ) {
    const summary = await this.codeReviewService.getProjectReviewSummary(projectId, periodType, periodValue);
    return {
      success: true,
      data: summary
    };
  }
}