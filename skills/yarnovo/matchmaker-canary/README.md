# matchmaker

交友平台 CLI（生产 https://matchmaker.agentaily.com）。装了之后可以和你的 Claude 对话式注册、填资料（性别、年龄、城市、兴趣、自我介绍），然后让你的 agent 直接用受限只读 SQL 查其他人匹配 + 发消息 + 收消息 + 读回执。中心化 Postgres，手机号 + 短信验证码登录，服务端只管存数据 + 开查询 + 存消息，匹配智能由你的 agent 自己决定。
TRIGGER when: 用户说"交友"、"找对象"、"matchmaker"、"注册交友平台"、"填交友资料"、"更新交友 profile"、"匹配异性"、"查谁喜欢 X"、"给交友站某人发消息"、"收交友站消息"。
DO NOT TRIGGER when: 用户要做聊天室 / 社交网络 / 匿名社区 / 陌生人交友 app（这些都不是本项目职能）；用户只想查数据库概念（用 sql-helper 之类）；服务端不可达时（curl /healthz 一次，down 就告诉用户稍后再试）。


## Install

```bash
# via clawhub
clawhub install matchmaker

# via skills.sh
npx skills add acong-tech/skill-matchmaker
```

## Version

Current: `0.1.0-canary.2`

## License

MIT-0. Published from https://github.com/acong-tech/skill-matchmaker by [skill-publish-cli](https://github.com/acong-tech/skill-publish-cli).
