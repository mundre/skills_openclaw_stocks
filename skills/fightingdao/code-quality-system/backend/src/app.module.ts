import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { PrismaModule } from './common/prisma.module';
import { DashboardModule } from './modules/dashboard/dashboard.module';
import { DataModule } from './modules/data/data.module';
import { ProjectsModule } from './modules/projects/projects.module';
import { TeamsModule } from './modules/teams/teams.module';
import { UsersModule } from './modules/users/users.module';
import { CodeReviewModule } from './modules/code-review/code-review.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    PrismaModule,
    DashboardModule,
    DataModule,
    ProjectsModule,
    TeamsModule,
    UsersModule,
    CodeReviewModule,
  ],
})
export class AppModule {}