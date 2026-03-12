#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  consumer) cat << 'PROMPT'
You are an expert. Help with: 消费者投诉. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  landlord) cat << 'PROMPT'
You are an expert. Help with: 房东/租房纠纷. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  employer) cat << 'PROMPT'
You are an expert. Help with: 劳动争议. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  insurance) cat << 'PROMPT'
You are an expert. Help with: 保险理赔. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  bank) cat << 'PROMPT'
You are an expert. Help with: 银行投诉. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  template) cat << 'PROMPT'
You are an expert. Help with: 模板库. Provide detailed, practical output in Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Dispute Letter — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  consumer        消费者投诉
  landlord        房东/租房纠纷
  employer        劳动争议
  insurance       保险理赔
  bank            银行投诉
  template        模板库

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
