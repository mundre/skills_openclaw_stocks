import { Controller, Get, Post, Put, Delete, Param, Body, Query, NotFoundException, ConflictException } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { TeamsService } from './teams.service';
import { PeriodQueryDto } from '../../common/dto/common.dto';
import { CreateTeamDto, UpdateTeamDto, CreateMemberDto } from './dto/teams.dto';

@ApiTags('小组管理')
@Controller('api/v1/teams')
export class TeamsController {
  constructor(private readonly teamsService: TeamsService) {}

  @Get()
  @ApiOperation({ summary: '获取小组列表' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getTeamList() {
    return this.teamsService.getTeamList();
  }

  @Get('available-users')
  @ApiOperation({ summary: '获取可用用户列表（未分配小组的）' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getAvailableUsers() {
    return this.teamsService.getAvailableUsers();
  }

  @Get('user-names')
  @ApiOperation({ summary: '获取所有小组成员的用户名列表（用于Git提交匹配）' })
  @ApiResponse({ status: 200, description: '获取成功' })
  async getUserNames() {
    return this.teamsService.getUserNames();
  }

  @Post()
  @ApiOperation({ summary: '创建小组' })
  @ApiResponse({ status: 201, description: '创建成功' })
  @ApiResponse({ status: 409, description: '小组名称已存在' })
  async createTeam(@Body() dto: CreateTeamDto) {
    try {
      return await this.teamsService.createTeam(dto);
    } catch (error) {
      if (error instanceof ConflictException) {
        throw error;
      }
      throw error;
    }
  }

  @Get(':id')
  @ApiOperation({ summary: '获取小组详情' })
  @ApiResponse({ status: 200, description: '获取成功' })
  @ApiResponse({ status: 404, description: '小组不存在' })
  async getTeamDetail(@Param('id') id: string) {
    try {
      return await this.teamsService.getTeamDetail(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw error;
    }
  }

  @Put(':id')
  @ApiOperation({ summary: '更新小组' })
  @ApiResponse({ status: 200, description: '更新成功' })
  @ApiResponse({ status: 404, description: '小组不存在' })
  @ApiResponse({ status: 409, description: '小组名称已存在' })
  async updateTeam(@Param('id') id: string, @Body() dto: UpdateTeamDto) {
    try {
      return await this.teamsService.updateTeam(id, dto);
    } catch (error) {
      if (error instanceof NotFoundException || error instanceof ConflictException) {
        throw error;
      }
      throw error;
    }
  }

  @Delete(':id')
  @ApiOperation({ summary: '删除小组' })
  @ApiResponse({ status: 200, description: '删除成功' })
  @ApiResponse({ status: 404, description: '小组不存在' })
  async deleteTeam(@Param('id') id: string) {
    try {
      return await this.teamsService.deleteTeam(id);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw error;
    }
  }

  @Post(':id/members')
  @ApiOperation({ summary: '为小组添加成员' })
  @ApiResponse({ status: 201, description: '添加成功' })
  @ApiResponse({ status: 404, description: '小组不存在' })
  async addMember(
    @Param('id') id: string,
    @Body('username') username: string,
    @Body('email') email?: string,
    @Body('isLeader') isLeader?: boolean,
  ) {
    try {
      return await this.teamsService.addMember(id, username, email, isLeader);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw error;
    }
  }

  @Delete(':id/members/:userId')
  @ApiOperation({ summary: '从小组移除成员' })
  @ApiResponse({ status: 200, description: '移除成功' })
  @ApiResponse({ status: 404, description: '用户不在该小组中' })
  async removeMember(@Param('id') id: string, @Param('userId') userId: string) {
    try {
      return await this.teamsService.removeMember(id, userId);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw error;
    }
  }

  @Get(':id/report')
  @ApiOperation({ summary: '获取小组报告' })
  @ApiResponse({ status: 200, description: '获取成功' })
  @ApiResponse({ status: 404, description: '小组不存在' })
  async getTeamReport(@Param('id') id: string, @Query() dto: PeriodQueryDto) {
    try {
      return await this.teamsService.getTeamReport(id, dto);
    } catch (error) {
      if (error instanceof NotFoundException) {
        throw error;
      }
      throw error;
    }
  }
}