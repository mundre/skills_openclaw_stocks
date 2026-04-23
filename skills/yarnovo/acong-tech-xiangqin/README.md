# xiangqin — 相亲平台 agent skill

通用 agent skill：让 agent 帮用户在 xiangqin 平台完成相亲 /
查匹配 / 发私信等。**不挑 agent runtime**（Claude Code /
OpenClaw / 其它支持 SKILL.md 协议的框架都能装）。

## 使用

1. 装这个 skill 到你的 agent 目录（每个 runtime 的 install
   命令不同，看各自文档）
2. 装配套 CLI：`pip install acong-tech-xiangqin` 或
   `uv tool install acong-tech-xiangqin`
3. agent 读到 SKILL.md 后，下次用户说"找对象 / 发私信 /
   查收件箱"等触发词时会自动调用 `xq` CLI

详见 [SKILL.md](./SKILL.md) 里的 TRIGGER 列表和典型流程。

## 协议

MIT-0（可自由使用 / 修改 / 再分发，无须署名）。
