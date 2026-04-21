/**
 * 如祺出行 Skill 配置文件
 */
const config = {
  // 环境变量配置
  env: {
    test: "test",
    uat: "uat",
    prod: "prod",
  },

  // API 服务基础 URL 配置
  baseUrl: {
    test: "https://testdocker-clientapi.ruqimobility.com/mcp/v1",
    uat: "https://uatdocker-clientapi.ruqimobility.com/mcp/v1",
    prod: "https://client.ruqimobility.com/mcp/v1",
  },

  // 乘客 H5 地址配置
  passengerH5Host: {
    test: "https://webtest.ruqimobility.com",
    uat: "https://webrel.ruqimobility.com",
    prod: "https://web.ruqimobility.com",
  },

  // 公共固定参数
  commonParams: {
    platform: "MINIPROGRAM_ANDROID",
  },

  // 订单状态描述
  statusDescriptions: {
    3: "指派中",
    4: "已接单",
    5: "已发车",
    6: "已到达",
    7: "服务中",
    8: "服务已结束",
    9: "已完成",
    10: "已取消",
    17: "免密待支付",
    18: "待支付",
  },
};

/**
 * 获取环境配置
 */
function getEnvConfig() {
  const env = "prod";
  const token = process.env.RUQI_CLIENT_MCP_TOKEN;

  return {
    env,
    token: token || null,
    baseUrl: config.baseUrl[env] || config.baseUrl.test,
    passengerH5Host: config.passengerH5Host[env] || config.passengerH5Host.test,
  };
}

export { config, getEnvConfig };
