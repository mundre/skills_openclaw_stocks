import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Response<T> {
  success: boolean;
  data: T;
  meta?: {
    total: number;
    page: number;
    limit: number;
    hasMore: boolean;
  };
}

@Injectable()
export class TransformInterceptor<T>
  implements NestInterceptor<T, Response<T>>
{
  intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Observable<Response<T>> {
    return next.handle().pipe(
      map((data) => {
        // 如果数据已经是标准格式，直接返回
        if (data && data.success !== undefined) {
          return data;
        }

        // 否则包装成标准格式
        return {
          success: true,
          data,
        };
      }),
    );
  }
}