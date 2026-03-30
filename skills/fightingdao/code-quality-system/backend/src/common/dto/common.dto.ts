import { ApiProperty } from '@nestjs/swagger';
import { IsOptional, IsString, IsIn, IsNumber, Min } from 'class-validator';

export class PaginationDto {
  @ApiProperty({ description: '页码', default: 1, required: false })
  @IsOptional()
  @IsNumber()
  @Min(1)
  page?: number = 1;

  @ApiProperty({ description: '每页数量', default: 10, required: false })
  @IsOptional()
  @IsNumber()
  @Min(1)
  limit?: number = 10;
}

export class PeriodQueryDto {
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