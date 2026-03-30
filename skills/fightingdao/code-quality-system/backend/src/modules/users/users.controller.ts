import { Controller, Get, Param, Query } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { UsersService } from './users.service';
import { UserAnalysisQueryDto } from './dto/users.dto';

@ApiTags('用户分析')
@Controller('api/v1/users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get(':id/analysis')
  @ApiOperation({ summary: '获取用户分析数据' })
  @ApiResponse({ status: 200, description: '获取成功' })
  @ApiResponse({ status: 404, description: '用户不存在' })
  async getUserAnalysis(
    @Param('id') id: string,
    @Query() dto: UserAnalysisQueryDto,
  ) {
    return this.usersService.getUserAnalysis(id, dto);
  }
}