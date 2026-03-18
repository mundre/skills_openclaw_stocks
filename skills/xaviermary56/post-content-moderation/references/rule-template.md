# Rule Template

Use this template when a user wants to customize moderation rules for a specific project, community, or platform.

## Minimal template

```text
审核对象：标题 / 正文 / 图片 / 视频 / 全部
白名单：
- 允许出现的品牌、账号、域名、术语、官方二维码、指定场景

默认拦截：
- 广告
- 联系方式

新增禁止词：
- 

新增禁止场景：
- 

明确放行场景：
- 

媒体规则：
- 图片是否允许二维码
- 视频是否允许口播联系方式
- 是否允许官方水印
- 是否允许站外引导文案

输出格式：
- 仅给结论
- 给结论+原因
- 给结论+原因+改写建议
- 返回 JSON 结果

冲突处理：
- 优先白名单 / 优先拦截 / 冲突时人工复核
```

## Example

```text
审核对象：全部
白名单：
- Apple、华为
- 官方域名 example.com
- 官方客服微信 service_official，仅限售后
- 官方售后二维码，仅限售后说明图

默认拦截：
- 广告
- 联系方式

新增禁止词：
- 返利
- 代发
- 保过

新增禁止场景：
- 招代理
- 引导站外交易
- 图中出现个人联系方式
- 视频结尾引导扫码

明确放行场景：
- 合法售后说明
- 官方公告

媒体规则：
- 普通帖子图片不允许出现二维码
- 视频不允许出现个人微信、手机号、群号
- 官方账号水印可保留

输出格式：
- 给结论+原因+改写建议

冲突处理：
- 冲突时人工复核
```

## Normalization guidance

Convert the user's free-form rules into a short reusable policy. Keep rules concrete and narrow. Avoid broad whitelisting such as "所有品牌都允许" unless the user explicitly insists.
