---
name: telegram-group-moderation
version: 0.9.0
description: Moderate Telegram groups with a bot by receiving message/webhook events, extracting text/caption/media context, applying anti-advertising and anti-contact policies, and deciding whether to pass, delete, warn, mute, ban, or send for manual review. Use when connecting Telegram groups or channels to an existing moderation system, especially when reusing post-content-moderation as the policy core.
emoji: 📱
homepage: https://github.com/XavierMary56/OmniPublish
requires:
  - post-content-moderation
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# Telegram Group Moderation

Build Telegram group moderation as an **integration layer**, not as a replacement for your existing moderation policy skill.

Recommended architecture:
- use `post-content-moderation` as the moderation-policy core
- use this skill to receive Telegram updates, normalize Telegram payloads, call the moderation core, and execute Telegram moderation actions

## Core responsibilities

Use this skill for:
- Telegram Bot webhook integration
- Telegram group message normalization
- extracting text, caption, media URL/file metadata, sender info, and chat info
- mapping moderation results into Telegram actions
- enforcing group-specific whitelist / admin-exemption / punishment rules
- logging moderation decisions for audit

Do not bloat this skill with generic moderation policy text that already belongs in `post-content-moderation`.

## Recommended decision flow

1. Receive Telegram update.
2. Detect update type:
   - message
   - edited_message
   - channel_post
   - edited_channel_post
3. Extract moderation input:
   - chat_id
   - message_id
   - user_id
   - username / display name
   - text
   - caption
   - photo / video presence
   - forwarded / reply / sticker / invite-link hints if needed
4. Normalize into a moderation payload.
5. Call moderation core.
6. Map result into Telegram action:
   - `pass` -> no action
   - `reject` -> delete / warn / mute / ban depending on rule set
   - `review` -> flag to admin channel or log queue
7. Persist result and evidence.

## Action mapping

Use clear business mapping. Example:
- `pass` -> allow
- `reject` + high risk -> delete message and warn user
- `reject` + repeated violations -> delete and mute
- `reject` + explicit scam/spam pattern -> delete and ban
- `review` -> forward summary to admin review channel

Keep action policy configurable per group.

## Telegram-specific rule inputs

Add these rule dimensions on top of the generic moderation core:
- allowed chat ids
- admin / moderator user whitelist
- trusted service bots whitelist
- punishment ladder by offense count
- whether edited messages should be re-audited
- whether forwarded posts are allowed
- whether links are fully blocked or only ad-like links are blocked
- whether usernames / bios / display names count as diversion evidence

## Media limitations

Telegram integration often needs more than plain text:
- image moderation may require OCR and QR detection
- video moderation may require frame extraction and subtitle/ASR pipeline
- file_id alone is not enough for real moderation; fetch or proxy media only when policy and privacy requirements allow it

If real media inspection is not implemented, document that clearly and avoid claiming full image/video moderation coverage.

## Security baseline

- validate Telegram webhook authenticity at the integration layer
- verify chat allowlist before processing
- keep bot token and API keys only in environment variables
- rate-limit admin actions and callback retries
- log delete/mute/ban actions with chat_id, user_id, message_id, and moderation reason
- avoid downloading media to unsafe temp paths
- define retention policy for moderated content snapshots

## Bundled references

Read these files as needed:
- `references/architecture.md` for recommended system design
- `references/telegram-event-mapping.md` for Telegram update normalization
- `references/action-policy.md` for pass/reject/review to delete/warn/mute/ban mapping
- `references/php-yaf-integration.md` for PHP 7.3 / Yaf-oriented integration notes
- `references/multi-language-integration.md` for Python, Go, and Java integration guidance
- `references/install-and-usage.zh-CN.md` for practical Chinese installation and configuration guidance
- `references/production-rollout.zh-CN.md` for production rollout boundaries and deployment advice
- `references/http-contract-example.json` for request/response contract example with moderation core
- `references/http-contract-production.zh-CN.md` for production HTTP contract guidance
- `references/http-contract-production-v2.zh-CN.md` for trace_id-aware production contract guidance
- `references/redis-db-offense-store.zh-CN.md` for Redis/DB offense-count design guidance
- `references/db-schema-example.sql` for default DB offense-log schema
- `references/audit-log-schema-example.sql` for audit-log schema
- `references/audit-log-rollout.zh-CN.md` for audit-log rollout guidance
- `references/config-template.env.example` for environment template hints
- `references/release-notes.zh-CN.md` for Chinese release notes
- `references/clawhub-release-copy.zh-CN.md` for Chinese release copy and page wording

## Bundled scripts

Use bundled scripts as starting points, not production-final code:
- `scripts/config.php` for env-driven config layout
- `scripts/telegram_support.php` for shared constants and helpers
- `scripts/telegram_webhook_example.php` for PHP webhook entry example
- `scripts/telegram_action_example.php` for PHP Telegram Bot API action calls
- `scripts/python_telegram_webhook_example.py` for Python webhook/action flow example
- `scripts/go_telegram_webhook_example.go` for Go webhook/action flow example
- `scripts/java_telegram_webhook_example.java` for Java webhook/action flow example

## Packaging guidance

Keep this skill platform-specific and small:
- Telegram ingress and action logic belongs here
- reusable moderation policy belongs in `post-content-moderation`
- if you later add Discord/WhatsApp, create separate integration skills instead of mixing all platforms into one
