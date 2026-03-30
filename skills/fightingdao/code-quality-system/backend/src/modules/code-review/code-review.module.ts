import { Module } from '@nestjs/common';
import { CodeReviewController } from './code-review.controller';
import { CodeReviewService } from './code-review.service';
import { PrismaModule } from '../../common/prisma.module';

@Module({
  imports: [PrismaModule],
  controllers: [CodeReviewController],
  providers: [CodeReviewService],
  exports: [CodeReviewService]
})
export class CodeReviewModule {}