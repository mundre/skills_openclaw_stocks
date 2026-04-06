#!/usr/bin/env node
import { execSync } from 'child_process';

const QR_FILES = {
  auth: 'https://p0.pipi.cn/mediaplus/fe_rock_web/e429583d52977e4a18bd6d11feec25cee87c1.png?imageMogr2/thumbnail/2500x2500%3E',
  pay: 'https://p0.pipi.cn/mediaplus/fe_rock_web/e429583dfcf05184575b289615216d59ea89a.png?imageMogr2/thumbnail/2500x2500%3E'
};

async function main() {
  try {
    // ================================
    // 正确读取 OpenClaw 传入格式
    // ================================
    let inputData = '';
    process.stdin.setEncoding('utf8');
    for await (const chunk of process.stdin) inputData += chunk;

    // 这是 OpenClaw 真实传入结构
    const [inputText, fullParams] = JSON.parse(inputData);
    const context = fullParams?.context || {};
    const args = fullParams?.args || {};

    // 现在 100% 能拿到
    const channel = context.channel;
    const targetId = context.targetId;

    console.log("✅ channel =", channel);
    console.log("✅ targetId =", targetId);

    if (!channel || !targetId) {
      console.error(JSON.stringify({ error: "拿不到渠道或ID" }));
      return;
    }

    // 优先从 args.qrType 获取，其次从 inputText 判断，默认 auth
    let qrType = args?.qrType;
    if (!qrType) {
      qrType = (inputText.includes("pay") || inputText.includes("支付")) ? "pay" : "auth";
    }
    
    const messageText = qrType === "pay" ? "" : "";
    const qrPath = QR_FILES[qrType];

    // 1. 发送二维码图片
    const cmd = `
      openclaw message send \
        --channel "${channel}" \
        --target "${targetId}" \
        --media "${qrPath}" \
        --message "${messageText.replace(/"/g, '\\"')}"`
    ;

    execSync(cmd);

    // 2. 发送链接（纯链接，无废话）
    const linkUrl = qrType === "pay"
      ? "https://deeplink.maoyan.com/asgard/app?type=weapp&to=%2Fpages%2Forder%2Findex%3FmerCode%3D1000545%26utm_source%3Dopenclaw"
      : "https://m.maoyan.com/mtrade/openclaw/token";
    const feishulink = qrType === "pay" ? 'https://m.maoyan.com/mtrade/order/list?merCode=1000545&utm_source=openclaw' : 'https://m.maoyan.com/mtrade/openclaw/token';

    const title = qrType === "pay" ? "请长按识别二维码前往支付页面或" : "请长按识别二维码获取认证密钥或";
    const desc = qrType === "pay" ? "👉 点击前往支付" : "👉 点击获取认证密钥";
    let tipCmd;

    if (channel.includes('weixin') || channel.includes('wx')) {
      tipCmd = `
        openclaw message send \
        --channel "${channel}" \
        --target "${targetId}" \
        --message "${title} [${desc}](${linkUrl})"
      `;
    } else {
      tipCmd = `
        openclaw message send \
        --channel "${channel}" \
        --target "${targetId}" \
        --message "${title} [${desc}](${feishulink})"
      `;
    }

    execSync(tipCmd);

    console.log(JSON.stringify({ success: true, qrType, message: messageText }));

  } catch (e) {
    console.error(JSON.stringify({ error: e.message }));
  }
}

main();