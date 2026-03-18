---
name: post-content-moderation
description: Review, rewrite, and moderate user-generated posts across title, body text, images, and videos to block ads and contact information while allowing configurable whitelist exceptions and project-specific custom rules. Use when checking community posts, feed submissions, comments with media, short-video captions, image/video attachments, or any post package before publishing, rejecting, or returning a moderation reason.
---

# Post Content Moderation

## Overview

Apply a strict moderation workflow to the full post package, not just plain text. Default goal: review title, body content, images, and videos together, then reject content that contains advertising intent or contact information unless the match falls inside an explicit whitelist or a user-provided custom rule.

## Quick operating modes

Choose one mode before moderating:

### 1. Strict full-auto mode

Use when the business requires no human intervention.

Rule:
- clear violation -> `拒绝`
- clear clean content -> `通过`
- ambiguous but risky -> `拒绝`
- media unreadable / model output invalid / upstream failed -> `拒绝`

### 2. Balanced mode

Use when manual review is available.

Rule:
- clear violation -> `拒绝`
- clear clean content -> `通过`
- ambiguous or partially unreadable -> `需人工复核`

## Moderation scope

Always review every available part of a post:
- 标题
- 正文
- 图片
- 视频
- 图片或视频内可见文字
- 配文、字幕、贴纸文字、水印、角标、二维码、头像/昵称引流信息

Do not approve a post only because the body text is clean. If any one component violates policy, the whole post should normally be marked `拒绝` or `需人工复核`.

## Field-specific rules

### 标题规则

Reject or review titles that contain:
- direct promotion, recruitment, rebate, agency, commission, guaranteed results
- diversion language such as "私聊", "加我", "主页联系", "扫码了解"
- visible contact IDs, domain names, or disguised contact phrases
- exaggerated ad-style hooks whose main purpose is conversion rather than discussion

### 正文规则

Reject or review body text that contains:
- product/service promotion with obvious conversion intent
- calls to contact off-platform or move to private chat
- direct or disguised联系方式
- repeated promotional copy, pricing slogans, or enrollment / agency / lead-generation language

### 图片规则

Reject or review images that contain:
- QR codes, mini-program codes, payment codes, group invite codes
- contact cards, business cards, chat screenshots, profile screenshots
- watermarks with account IDs, brands plus CTA, or sales copy
- posters with price, discount, recruitment, or diversion wording
- corner text, decorative background text, or hidden overlaid text carrying contact or ad signals

### 视频规则

Reject or review videos that contain:
- cover image text with promotion or contact details
- subtitles or spoken content that guide users off-platform
- opening cards, ending cards, or fixed watermarks with contact info
- flash frames showing QR codes, account IDs, phone numbers, or group invitations
- oral CTA such as "想了解私信我" / "主页联系" / "加V备注"

## Default moderation policy

Treat the following as violations unless explicitly whitelisted:

### 1. Advertising / promotion

Block content that obviously promotes:
- products, services, channels, groups, websites, apps, stores, or paid offers
- traffic diversion such as "加我", "私聊了解", "点击链接", "扫码进群", "代理/加盟/返利/推广"
- recruitment, lead collection, account selling, brushing orders, betting, gray-market promotion, or obvious marketing copy
- repeated brand exposure plus calls to action
- image or video overlays that guide users to off-platform contact or purchase

Common ad signals:
- strong call-to-action language
- price, discount, rebate, agency, invitation, commission, guaranteed results
- external platform redirection
- excessive emoji / symbols used for promotion
- intentionally obfuscated promotional wording
- promotional subtitles, end cards, cover text, or watermark copy

### 2. Contact information

Block direct or disguised contact details, including:
- phone or mobile numbers
- WeChat / VX / V / vx / wx variants
- QQ numbers or QQ group numbers
- email addresses
- URLs, domains, short links, QR-code invitations expressed in text or shown in media
- Telegram, WhatsApp, Line, Discord, Skype, social account IDs
- platform handles or IDs whose clear purpose is off-platform contact
- QR codes, payment codes, contact cards, business cards, profile screenshots, or group invitation screenshots

Also treat as violations when contact information is deliberately obfuscated, for example:
- replacing digits with spaces, symbols, Chinese numerals, or homophones
- mixing letters and punctuation to bypass detection
- replacing keywords with variants such as `v`, `vx`, `wx`, `薇`, `微`, `卫星`, `扣扣`, `邮箱`, `油箱`
- splitting numbers across spaces or punctuation
- using Chinese numerals, homophones, or mixed scripts to hide IDs
- "微❤", "薇", "卫星", "扣扣", "油箱", "点我头像", "看签名"
- showing contact text only in image corners, cover image, video ending card, or subtitle frames

## Multi-modal review workflow

For each moderation task, follow this order:

1. Review title.
2. Review body text.
3. Review each image for:
   - visible text
   - QR codes
   - watermarks
   - contact cards / screenshots / profile clues
   - promotional posters or pricing posters
4. Review each video for:
   - spoken or subtitled contact info
   - cover image text
   - opening/ending cards
   - watermarks and persistent corner text
   - QR codes or account IDs shown in frames
5. Merge findings across all components.
6. Check whitelist and custom rules.
7. Produce one final result: `通过`, `拒绝`, or `需人工复核`.

## Quick decision tree

Use this shortcut when speed matters:

- any clear contact info in title/body/image/video -> `拒绝`
- any clear ad/diversion language in title/body/image/video -> `拒绝`
- whitelist clearly covers the matched content and scenario -> `通过`
- model cannot inspect a required field:
  - strict full-auto -> `拒绝`
  - balanced mode -> `需人工复核`
- no hit across all fields -> `通过`

## Cross-field judgment rule

Judge the post as a whole.

Examples:
- title is normal but image contains a WeChat ID -> reject
- body is normal but video end card says "扫码领取" -> reject
- image shows a QR code but context is unclear and whitelist is absent -> manual review
- title/body mention a brand normally, but video repeatedly induces purchase or contact -> reject

## Whitelist handling

Whitelist is an exception layer, not a blanket bypass.

Allow content when the whitelist clearly covers the matched item, for example:
- allowed brand names
- allowed official accounts or official domains
- approved merchant names
- approved phrases that would otherwise look promotional
- internal business terms that resemble blocked words
- approved official QR codes or approved official service accounts in a narrowly defined scenario

Apply whitelist with these constraints:
- whitelist only the exact item or exact scenario the user approved
- do not expand a narrow whitelist into a broad exemption
- if promotional intent still exists outside the whitelisted fragment, reject
- if the post contains extra contact details beyond the whitelist scope, reject or send to manual review
- if only one image/video asset is whitelisted, do not automatically whitelist all assets in the same post

If the user says "可以自己定义自己的规则", ask for or accept custom rules in plain language and merge them after the default policy.

## Result priority

Use these priorities:
- clear ad or contact evidence in any field -> `拒绝`
- weak or ambiguous evidence, especially in image/video details -> `需人工复核`
- all fields clean, or only narrowly whitelisted content appears -> `通过`

## Standard output

Prefer this fixed output:

```text
审核结果：通过 / 拒绝 / 需人工复核
风险等级：低 / 中 / 高
审核范围：标题 / 正文 / 图片 / 视频
命中字段：标题 / 正文 / 图片 / 视频
命中位置：标题 / 正文第2段 / 第1张图片右下角 / 视频封面 / 视频00:12字幕 / 视频结尾等
命中规则：广告 / 联系方式 / 白名单例外 / 自定义规则
原因：一句话说明核心依据
处理建议：通过发布 / 删除违规文案 / 替换图片 / 裁剪视频片段 / 转人工复核
改写建议：如需，给出可发布版本
```

### Risk level guidance

- `高`：明确广告、明确联系方式、明确二维码、明确引流
- `中`：存在明显嫌疑但证据不完整，或有混淆空间
- `低`：未命中风险，仅正常讨论或明确白名单放行

## JSON output option

If the user requests structured output, use:

```json
{
  "result": "pass|reject|review",
  "risk_level": "low|medium|high",
  "scope": ["title", "body", "images", "video"],
  "hits": [
    {
      "field": "image",
      "position": "image_1_bottom_right",
      "rule": "contact_info",
      "evidence": "VX: abc123456"
    }
  ],
  "reason": "image contains off-platform contact information",
  "action": "replace_image"
}
```

## Rewrite behavior

When asked to revise a rejected post:
- remove ad-like calls to action
- remove all contact information and diversion hints
- remove or replace violating images/videos when needed
- preserve the user's main legitimate meaning
- keep wording natural, not robotic
- do not silently keep risky borderline phrases
- if media itself is违规, state that the media asset must be removed or replaced

## Custom rule intake

When the user provides extra moderation rules, normalize them into this structure before applying:

```text
审核对象：标题 / 正文 / 图片 / 视频 / 全部
白名单：<allowed words / brands / accounts / domains / QR codes / scenarios>
禁止词：<extra banned words>
禁止场景：<extra banned behaviors>
放行场景：<explicitly allowed contexts>
媒体规则：<special image/video rules>
输出要求：<whether to rewrite, label, explain, or return JSON>
```

If custom rules are incomplete, still perform moderation with defaults and state which defaults were used.

## Media-specific guidance

### Images

Pay extra attention to:
- posters, flyers, screenshots, chat records, contact cards
- QR codes, mini-program codes, payment codes
- watermarks with account IDs or brand recruitment copy
- text hidden in corners, borders, or background decorations

### Videos

Pay extra attention to:
- cover image text
- subtitles and speech transcription
- opening/ending cards
- repeated corner watermarks
- flash frames showing contact info
- spoken diversion like "私信我" or "主页联系"

If video cannot be fully inspected, do not guess. Return `需人工复核` and specify what could not be confirmed.

## Examples

### Example 1: reject because image contains contact info

Input:

```text
标题：今天分享一下我的护肤心得
正文：最近换季，保湿真的很重要。
图片：海报右下角含“VX: abc123456”
```

Output:

```text
审核结果：拒绝
风险等级：高
审核范围：标题、正文、图片
命中字段：图片
命中位置：第1张图片右下角
命中规则：联系方式
原因：图片中存在微信联系方式，构成站外引流。
处理建议：替换图片
建议：删除或替换该图片后再发布。
```

### Example 2: reject because video end card is promotional

Input:

```text
标题：兼职经验分享
正文：最近试了几个渠道。
视频：结尾出现“想了解更多，扫码进群”
```

Output:

```text
审核结果：拒绝
风险等级：高
审核范围：标题、正文、视频
命中字段：视频
命中位置：视频结尾
命中规则：广告、联系方式
原因：视频结尾包含明显引流和扫码进群信息。
处理建议：裁剪或替换违规片段
建议：移除结尾引流片段并删除相关联系方式。
```

### Example 3: whitelist exception

Input rule:

```text
白名单：官方客服微信 service_official，仅用于售后说明；官方售后二维码，仅限订单售后页面展示
```

Input content:

```text
标题：售后处理说明
正文：如订单异常，请联系官方客服处理。
图片：展示官方售后二维码
```

Output:

```text
审核结果：通过
风险等级：低
审核范围：标题、正文、图片
命中字段：图片
命中位置：第1张图片
命中规则：白名单例外
原因：命中的二维码属于明确白名单，且场景限于官方售后说明。
处理建议：通过发布
```

## References

- Read `references/rule-template.md` when converting user-provided business rules into a reusable moderation policy.
- Read `references/install-and-usage.md` when the user asks how to install, import, distribute, or operate this skill in a workspace.
- Read `references/api-integration.md` when the user wants pull APIs, callback APIs, comment moderation APIs, or a fully automatic no-human-review moderation workflow.
- Read `references/api-spec.md` when the user needs a backend-facing API contract with request fields, response fields, error codes, action enums, and implementation flow.
- Read `references/prompt-templates.md` when the user needs reusable moderation prompts, JSON-only response constraints, or full-auto conservative suffixes.
- Read `references/php-example-notes.md` and use `scripts/php_xai_client_example.php` when the user wants a PHP 7.3 integration example for x.ai moderation, callback handling, or comment moderation.
- Read `references/php-demo-suite.md` and use the bundled scripts when the user wants runnable PHP demos for pull, audit, callback, and comment-review flows.
