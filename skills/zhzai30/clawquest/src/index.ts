import express, { type Request, type Response } from "express";
import { z } from "zod";
import { serverMine, getPlayerStatus } from "./tools.js";

const app = express();
app.use(express.json());

const requestSchema = z.object({
  playerToken: z.string().min(1),
  autoBuyStamina: z.boolean().optional()
});

/**
 * 处理工具调用入口，分发到对应的托管挖矿能力。
 */
app.post("/tool/:name", async (req: Request, res: Response) => {
  const parsed = requestSchema.safeParse(req.body ?? {});
  if (!parsed.success) {
    return res.status(400).json({ ok: false, error: "invalid_payload" });
  }

  const toolName = req.params.name;
  const payload = parsed.data;

  try {
    if (toolName === "server_mine") {
      const result = await serverMine(payload.playerToken, payload.autoBuyStamina);
      return res.json({ ok: true, data: result });
    }

    if (toolName === "get_player_status") {
      const result = await getPlayerStatus(payload.playerToken);
      return res.json({ ok: true, data: result });
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "tool_execution_failed";
    return res.status(502).json({ ok: false, error: errorMessage });
  }

  return res.status(404).json({ ok: false, error: "tool_not_found" });
});

/**
 * 健康检查接口，用于探活与部署检查。
 */
app.get("/health", (_req: Request, res: Response) => {
  res.json({ ok: true, service: "skill-openclaw-b" });
});

const port = Number(process.env.PORT ?? "4021");
/**
 * 启动 Skill HTTP 服务。
 */
app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`skill-openclaw-b listening on :${port}`);
});
