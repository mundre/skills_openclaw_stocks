#!/usr/bin/env node
/**
 * 如祺出行订单轮询脚本（带截图和消息推送）
 *
 * 用法:
 *   node scripts/ruqi_poll_with_screenshot.js --orderId <订单ID>
 *
 * 功能:
 *   - 查询订单状态
 *   - 订单状态变化时发送消息+截图
 *   - 距上次发送超过3分钟时发送消息+截图
 *   - 订单状态 > 8 时自动关闭浏览器并退出
 *
 * 流程:
 *
 *   ┌─────────────────────────┐
 *   │       开始轮询           │
 *   └───────────┬─────────────┘
 *               ▼
 *   ┌─────────────────────────┐
 *   │     查询订单状态          │
 *   └───────────┬─────────────┘
 *               ▼
 *   ┌─────────────────────────────────────┐
 *   │  状态变化 OR 距上次发送 > 3分钟？      │
 *   └─────┬───────────────────┬───────────┘
 *         │ 是                │ 否
 *         ▼                   ▼
 *   ┌───────────────┐   ┌─────────────┐
 *   │    截图        │   │   跳过发送   │
 *   └───────┬───────┘   └──────┬──────┘
 *           │                  │
 *           ▼                  │
 *   ┌───────────────┐          │
 *   │  发送消息+截图  │          │
 *   └───────┬───────┘          │
 *           │                  │
 *           ▼                  ▼
 *   ┌─────────────────────────────────────┐
 *   │        更新 lastStatus               │
 *   └───────────┬─────────────────────────┘
 *               ▼
 *   ┌─────────────────────────┐
 *   │     订单状态 > 8？        │
 *   └─────┬───────────┬───────┘
 *         │ 是        │ 否
 *         ▼           ▼
 *   ┌───────────┐  ┌─────────────┐
 *   │  结束轮询   │  │ 等待下一轮   │
 *   └───────────┘  └─────────────┘
 */

import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";
import fs from "fs";
import ruqiApi from "./ruqi_api.js";
import { config, getEnvConfig } from "./config.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * 轮询脚本配置
 * @property {string} deviceName - 模拟的移动设备名称
 * @property {string} screenshotDir - 截图保存目录
 * @property {number} pageLoadWait - 页面加载等待时间（毫秒）
 * @property {number} queryRetry - 订单查询重试次数
 * @property {number} queryRetryDelay - 查询重试间隔（毫秒）
 * @property {number} pollInterval - 轮询间隔（毫秒）
 * @property {number} notifyInterval - 通知间隔（毫秒）
 */
const POLL_CONFIG = {
  deviceName: "iPhone 12",
  screenshotDir: resolve(__dirname, "../tmp/screenshots"),
  pageLoadWait: 5000,
  queryRetry: 3,
  queryRetryDelay: 1000,
  pollInterval: 10 * 1000,
  notifyInterval: 2 * 60 * 1000,
};

/**
 * 确保截图目录存在，不存在则创建
 */
function ensureScreenshotDir() {
  if (!fs.existsSync(POLL_CONFIG.screenshotDir)) {
    fs.mkdirSync(POLL_CONFIG.screenshotDir, { recursive: true });
  }
}

/**
 * 清空截图目录中的所有图片
 */
function clearScreenshotDir() {
  if (!fs.existsSync(POLL_CONFIG.screenshotDir)) {
    return;
  }
  const files = fs.readdirSync(POLL_CONFIG.screenshotDir);
  let cleared = 0;
  for (const file of files) {
    if (file.endsWith(".png")) {
      fs.unlinkSync(resolve(POLL_CONFIG.screenshotDir, file));
      cleared++;
    }
  }
  if (cleared > 0) {
    log(`🧹 已清理 ${cleared} 张截图`);
  }
}

/**
 * 解析命令行参数
 * @returns {Object|null} 解析后的参数对象，包含 orderId
 */
function parseArguments() {
  const args = process.argv.slice(2);
  if (args.length < 1) return null;
  const params = {};
  const orderIdIndex = args.indexOf("--orderId");
  if (orderIdIndex !== -1 && orderIdIndex + 1 < args.length) {
    params.orderId = args[orderIdIndex + 1];
  }
  return params.orderId ? params : null;
}

/**
 * 等待指定毫秒数
 * @param {number} ms - 等待时间（毫秒）
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 带时间戳的日志输出
 * @param {string} message - 日志消息
 */
function log(message) {
  const timestamp = new Date().toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
  console.log(`[${timestamp}] ${message}`);
}

/**
 * 执行外部命令
 * @param {string} command - 要执行的命令
 * @param {string[]} args - 命令参数数组
 * @param {Object} options - 执行选项
 * @param {number} [options.timeout=30000] - 超时时间（毫秒）
 * @returns {Promise<string>} 命令输出的 stdout
 */
function execCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args, {
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: options.timeout || 30000,
    });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d) => (stdout += d.toString()));
    proc.stderr.on("data", (d) => (stderr += d.toString()));
    proc.on("close", (code) => {
      if (code === 0) resolve(stdout);
      else reject(new Error(stderr || `exit code ${code}`));
    });
    proc.on("error", reject);
  });
}

/**
 * 关闭浏览器
 */
async function closeBrowser() {
  try {
    await execCommand("agent-browser", ["close"], {
      timeout: 10000,
      shell: false,
    });
    log(`✅ 浏览器已关闭`);
  } catch (e) {
    log(`⚠️ 关闭浏览器失败: ${e.message}`);
  }
}

/**
 * 发送消息（支持纯文本或带图片）
 * @param {string} message - 消息内容
 * @param {string|null} [imagePath=null] - 图片路径（可选）
 */
async function sendMessage(message, imagePath = null) {
  const channel = process.env.RUQI_CHANNEL || "feishu";
  const target = process.env.RUQI_TARGET;

  if (!target) {
    log(`⚠️ RUQI_TARGET 未设置，跳过发送消息`);
    return;
  }

  const args = ["message", "send", "--message", message];

  if (imagePath) {
    args.push("--media", imagePath);
  }

  args.push("--channel", channel, "--target", target);

  await execCommand("openclaw", args, { timeout: 30000 });
}

/**
 * 订单结束状态消息映射
 * @property {Object} 9 - 已完成
 * @property {Object} 10 - 已取消
 * @property {Object} 17 - 免密待支付
 * @property {Object} 18 - 待支付
 */
const STATUS_END_MESSAGES = {
  9: { emoji: "🎉", text: "订单已完成，轮询结束" },
  10: { emoji: "❌", text: "订单已取消，轮询结束" },
  17: { emoji: "💳", text: "等待支付，轮询结束" },
  18: { emoji: "💳", text: "等待支付，轮询结束" },
};

/**
 * 轮询订单状态并发送截图
 * @param {string} orderId - 订单ID
 */
async function pollWithScreenshots(orderId) {
  log(`🚀 启动订单跟踪，订单ID: ${orderId}`);

  const envConfig = getEnvConfig();
  const orderUrl = `${envConfig.passengerH5Host}/busiClientWeb/index.html#/TripShare?orderId=${orderId}`;
  let pollCount = 0;

  let lastStatus = null;
  let lastSendTime = 0;

  let browserReady = false;
  try {
    log(`🌐 打开浏览器（${POLL_CONFIG.deviceName} 模式）...`);
    await execCommand(
      "agent-browser",
      ["set", "device", POLL_CONFIG.deviceName],
      { timeout: 10000 },
    );
    await execCommand("agent-browser", ["open", orderUrl], {
      timeout: 30000,
    });
    await sleep(POLL_CONFIG.pageLoadWait);
    browserReady = true;
    log(`✅ 浏览器已打开（${POLL_CONFIG.deviceName}），页面加载完成`);
  } catch (e) {
    log(`⚠️ 浏览器初始化失败，将使用纯文本模式: ${e.message}`);
  }

  try {
    while (true) {
      pollCount++;
      log(`📸 第 ${pollCount} 次轮询...`);

      let orderData = null;
      for (let retry = 0; retry < POLL_CONFIG.queryRetry; retry++) {
        try {
          orderData = await ruqiApi.query_ride_order({ orderId });
          break;
        } catch (e) {
          log(`⚠️ 查询失败，第 ${retry + 1} 次重试: ${e.message}`);
          if (retry < POLL_CONFIG.queryRetry - 1)
            await sleep(POLL_CONFIG.queryRetryDelay);
        }
      }

      const orderInfo = orderData?.content?.orderInfo;
      if (orderInfo) {
        const status = orderInfo.orderState;
        const statusDesc =
          config.statusDescriptions?.[status] || `状态(${status})`;
        log(`📊 订单状态: ${statusDesc}`);

        const statusChanged = status !== lastStatus;
        const timeElapsed =
          Date.now() - lastSendTime >= POLL_CONFIG.notifyInterval;
        const shouldNotify = statusChanged || timeElapsed || status > 8;

        if (shouldNotify) {
          let screenshotSuccess = false;
          let screenshotPath = null;

          if (browserReady) {
            screenshotPath = `${POLL_CONFIG.screenshotDir}/${orderId}_${Date.now()}.png`;
            try {
              await execCommand(
                "agent-browser",
                ["screenshot", screenshotPath],
                {
                  timeout: 30000,
                },
              );
              screenshotSuccess = true;
            } catch (e) {
              log(`⚠️ 截图失败: ${e.message}`);
            }
          }

          let message = `📸 订单轮询\n`;
          message += `订单ID: ${orderInfo.orderId}\n`;
          message += `状态: ${statusDesc}\n`;
          message += `起点: ${orderInfo.fromAddress}\n`;
          message += `终点: ${orderInfo.toAddress}\n`;

          if (orderData.content.driverInfo) {
            const driver = orderData.content.driverInfo;
            if (driver.driverName) message += `司机: ${driver.driverName}\n`;
            if (driver.driverPhone) message += `电话: ${driver.driverPhone}\n`;
            if (driver.carNumber)
              message += `车牌: ${driver.carNumber} ${driver.carColor || ""} ${driver.carModel || ""}\n`;
          }
          message += `[[📱 详情请打开如祺出行小程序查看](https://web.ruqimobility.com/ruqi/index.html#/download?to=service&pagePath=pages%2Findex%2Findex&toPlatform=miniApp&skipType=3)]`;

          try {
            if (screenshotSuccess) {
              await sendMessage(message, screenshotPath);
            } else {
              await sendMessage(message);
            }
            lastSendTime = Date.now();
            log(
              `📨 消息已发送（状态变化: ${statusChanged}, 超时通知: ${timeElapsed}）`,
            );
          } catch (e) {
            log(`❌ 发送消息失败: ${e.message}`);
          }
        } else {
          log(`⏭️ 跳过发送（状态未变化且未超时）`);
        }

        lastStatus = status;

        if (status > 8) {
          const endInfo = STATUS_END_MESSAGES[status];
          if (endInfo) {
            log(`${endInfo.emoji} ${endInfo.text}`);
          }
          // 清空截图文件夹
          clearScreenshotDir();
          break;
        }
      } else {
        log(`⚠️ 订单数据异常，等待后重试`);
      }

      await sleep(POLL_CONFIG.pollInterval);
    }
  } finally {
    await closeBrowser();
  }
}

/**
 * 主函数入口
 */
async function main() {
  try {
    const params = parseArguments();
    if (!params || !params.orderId) {
      console.log(
        `用法: node scripts/ruqi_poll_with_screenshot.js --orderId <订单ID>`,
      );
      process.exit(0);
    }
    const { orderId } = params;
    ensureScreenshotDir();
    await pollWithScreenshots(orderId);
    process.exit(0);
  } catch (error) {
    console.error(`错误: ${error.message}`);
    await closeBrowser();
    process.exit(1);
  }
}

main();
