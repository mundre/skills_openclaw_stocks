const gameApiBaseUrl = process.env.GAME_API_BASE_URL ?? "http://127.0.0.1:8080";
const requestTimeoutMilliseconds = Number(process.env.REQUEST_TIMEOUT_MS ?? "8000");

/**
 * 发起一次服务端托管挖矿请求。
 */
export async function serverMine(playerToken: string, autoBuyStamina?: boolean): Promise<unknown> {
  return await postJson("/openclaw/server/mine", playerToken, { autoBuyStamina });
}

/**
 * 查询玩家状态，供 Skill 决策使用。
 */
export async function getPlayerStatus(playerToken: string): Promise<unknown> {
  return await postJson("/openclaw/server/player_status", playerToken, {});
}

/**
 * 发送带 Bearer 鉴权的 JSON 请求，并统一处理超时与错误响应。
 */
async function postJson(path: string, playerToken: string, body: Record<string, unknown>): Promise<unknown> {
  const abortController = new AbortController();
  const timeoutHandle = setTimeout(() => {
    abortController.abort();
  }, requestTimeoutMilliseconds);

  try {
    const response = await fetch(`${gameApiBaseUrl}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${playerToken}`
      },
      body: JSON.stringify(body),
      signal: abortController.signal
    });

    const responseJson = await response.json();
    if (!response.ok) {
      throw new Error(
        `game_api_error status=${response.status} body=${JSON.stringify(responseJson)}`
      );
    }
    return responseJson;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(`game_api_timeout timeoutMs=${requestTimeoutMilliseconds}`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutHandle);
  }
}
