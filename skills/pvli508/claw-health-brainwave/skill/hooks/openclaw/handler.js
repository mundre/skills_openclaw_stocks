// OpenClaw Hook Handler
// 在消息到达时调用本地后端触发播放

export default async function handler(event) {
  // 仅处理 feishu 入站消息
  const text = event?.message?.text || event?.data?.text || '';
  const user_id = event?.sender?.open_id || event?.data?.user_id || '';

  if (!text) return {};

  // 调用本地后端 webhook（异步，不阻塞 agent 响应）
  fetch('http://localhost:3100/webhook/feishu', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, user_id }),
  }).catch(() => {});

  return {};
}
