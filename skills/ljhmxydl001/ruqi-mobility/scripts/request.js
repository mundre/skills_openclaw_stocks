/**
 * HTTP 请求封装 - 基于 axios
 */

import axios from "axios";
import { config, getEnvConfig } from "./config.js";

/**
 * 不需要 Token 的接口白名单
 */
const NO_TOKEN_ENDPOINTS = [
  "send_verification_code",
  "login_with_verification_code",
];

/**
 * 发送 HTTP 请求到如祺出行 API
 * @param {string} endpoint - 接口名称
 * @param {Object} requestData - 请求数据
 * @param {boolean} returnHeaders - 是否返回 headers（登录接口需要）
 */
export async function httpRequest(
  endpoint,
  requestData,
  returnHeaders = false,
) {
  const needsToken = !NO_TOKEN_ENDPOINTS.includes(endpoint);
  const envConfig = getEnvConfig();

  if (needsToken && !envConfig.token) {
    throw new Error("RUQI_CLIENT_MCP_TOKEN 环境变量未配置，请先登录");
  }

  // 自动添加公共参数
  const fullRequest = {
    ...config.commonParams,
    timestamp: Date.now(),
    ...(envConfig.token && { token: envConfig.token }),
    ...requestData,
  };

  // 构建完整请求体
  const requestBody = {
    jsonrpc: "2.0",
    id: Date.now().toString(),
    method: "tools/call",
    params: {
      name: endpoint,
      arguments: fullRequest,
    },
  };

  try {
    const response = await axios({
      method: "POST",
      url: envConfig.baseUrl,
      data: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 秒超时
    });

    // 解析嵌套结构: data.result.content[].text
    const content = response?.data?.data?.result?.content?.[0]?.text;

    if (content) {
      // 检查业务错误
      if (content.code !== 0) {
        throw new Error(
          `业务错误: ${content.message || JSON.stringify(content)}`,
        );
      }

      // 登录接口返回包含 headers 的完整响应
      if (returnHeaders) {
        return {
          data: content,
          headers: response.headers,
        };
      }

      return content;
    } else {
      // 打印完整响应用于调试
      console.error("响应数据:", JSON.stringify(response.data, null, 2));
      throw new Error("无效的响应格式");
    }
  } catch (error) {
    throw new Error("error: " + error);
  }
}
