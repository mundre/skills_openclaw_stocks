/**
 * Digital Life Organizer - 自测脚本
 */
import { handler } from '../index.js';

async function runTests() {
  console.log('开始测试...');
  const tests = [
    { name: 'scan_assets', expected: true },
    { name: 'organize_files', expected: true },
    { name: 'manage_subscriptions', expected: true },
    { name: 'audit_security', expected: true },
    { name: 'full_audit', expected: true },
    { name: 'unknown', expected: false }
  ];
  for (const t of tests) {
    const r = await handler({ action: t.name, params: {} });
    console.log((r.success === t.expected ? '✅' : '❌') + ' ' + t.name);
  }
  console.log('测试完成');
}
runTests().catch(console.error);
