/**
 * 性能测试 - 测试系统性能
 */

const Benchmark = require('benchmark');
const TaskManager = require('../core/task-manager');

describe('Performance Tests', () => {
  let taskManager;

  beforeAll(() => {
    taskManager = new TaskManager(':memory:');
  });

  afterAll(() => {
    taskManager.close();
  });

  describe('数据库操作性能', () => {
    test('创建 1000 个项目的性能', () => {
      const suite = new Benchmark.Suite('create-1000-projects');

      suite.add('批量创建', () => {
        const startTime = Date.now();
        for (let i = 0; i < 1000; i++) {
          taskManager.createProject({
            name: `Project ${i}`,
            github_url: `https://github.com/test/project-${i}`,
            description: `测试项目 ${i}`
          });
        }
        const endTime = Date.now();
        console.log(`创建 1000 个项目耗时：${endTime - startTime}ms`);
      });

      suite.on('cycle', (event) => {
        console.log(`Benchmark: ${event.target.stats.mean}ms`);
      });

      suite.run({ async: true });
    });

    test('查询任务的性能', () => {
      // 先创建一些测试数据
      const project = taskManager.createProject({
        name: 'Performance Test Project',
        github_url: 'https://github.com/test/perf-project',
        description: '性能测试项目'
      });

      for (let i = 0; i < 100; i++) {
        taskManager.createTask({
          projectId: project.id,
          name: `Task ${i}`,
          description: `测试任务 ${i}`,
          priority: i
        });
      }

      const suite = new Benchmark.Suite('query-tasks');

      suite.add('查询所有任务', () => {
        taskManager.getTasksByProject(project.id);
      });

      suite.add('查询特定状态任务', () => {
        taskManager.getTasksByStatus('pending');
      });

      suite.on('cycle', (event) => {
        console.log(`Benchmark: ${event.target.name} - ${event.target.stats.mean}ms`);
      });

      suite.run({ async: true });
    });

    test('批量插入性能对比', () => {
      const suite = new Benchmark.Suite('batch-insert');

      suite.add('单个插入', () => {
        const project = taskManager.createProject({
          name: `Single Insert Test`,
          github_url: `https://github.com/test/single-${Date.now()}`,
          description: '单个插入测试'
        });

        for (let i = 0; i < 100; i++) {
          taskManager.createTask({
            projectId: project.id,
            name: `Task ${i}`,
            description: `测试任务 ${i}`,
            priority: i
          });
        }
      });

      suite.on('cycle', (event) => {
        console.log(`Benchmark: ${event.target.stats.mean}ms`);
      });

      suite.run({ async: true });
    });
  });

  describe('缓存性能', () => {
    test('缓存命中率测试', () => {
      const project = taskManager.createProject({
        name: 'Cache Test Project',
        github_url: 'https://github.com/test/cache-project',
        description: '缓存测试项目'
      });

      const task = taskManager.createTask({
        projectId: project.id,
        name: 'Cache Test Task',
        description: '缓存测试任务',
        priority: 5
      });

      // 第一次查询（无缓存）
      const startTime1 = Date.now();
      taskManager.getTask(task.id);
      const endTime1 = Date.now();

      // 第二次查询（有缓存）
      const startTime2 = Date.now();
      taskManager.getTask(task.id);
      const endTime2 = Date.now();

      console.log(`无缓存查询耗时：${endTime1 - startTime1}ms`);
      console.log(`有缓存查询耗时：${endTime2 - startTime2}ms`);
      console.log(`性能提升：${((endTime1 - startTime1) / (endTime2 - startTime2)).toFixed(2)}x`);

      expect(endTime2 - startTime2).toBeLessThanOrEqual(endTime1 - startTime1);
    });
  });

  describe('并发性能', () => {
    test('并发创建任务', async () => {
      const project = taskManager.createProject({
        name: 'Concurrency Test Project',
        github_url: 'https://github.com/test/concurrency-project',
        description: '并发测试项目'
      });

      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          taskManager.createTask({
            projectId: project.id,
            name: `Concurrent Task ${i}`,
            description: `并发任务 ${i}`,
            priority: i
          })
        );
      }

      const startTime = Date.now();
      await Promise.all(promises);
      const endTime = Date.now();

      console.log(`并发创建 100 个任务耗时：${endTime - startTime}ms`);
      console.log(`平均每个任务：${((endTime - startTime) / 100).toFixed(2)}ms`);

      expect(endTime - startTime).toBeLessThan(1000); // 1 秒内完成
    });
  });

  describe('内存使用', () => {
    test('内存增长测试', () => {
      const initialMemory = process.memoryUsage().heapUsed;

      // 创建大量数据
      for (let i = 0; i < 1000; i++) {
        taskManager.createProject({
          name: `Memory Test Project ${i}`,
          github_url: `https://github.com/test/memory-${i}`,
          description: `内存测试项目 ${i}`
        });
      }

      const finalMemory = process.memoryUsage().heapUsed;
      const memoryGrowth = finalMemory - initialMemory;

      console.log(`初始内存：${(initialMemory / 1024 / 1024).toFixed(2)}MB`);
      console.log(`最终内存：${(finalMemory / 1024 / 1024).toFixed(2)}MB`);
      console.log(`内存增长：${(memoryGrowth / 1024 / 1024).toFixed(2)}MB`);

      // 内存增长应该在合理范围内
      expect(memoryGrowth).toBeLessThan(100 * 1024 * 1024); // 小于 100MB
    });
  });
});