#!/usr/bin/env node

/**
 * Calls GF hiAgentChat SSE API (agentId=mfis2agent) and outputs answer to stdout.
 * Only accepts the user's question as argument; no user/session context.
 * Requires GF_AGENT_COOKIE in env.
 */

const API_URL = 'https://aigctest.gf.com.cn/api/aigc/api/base/hiAgentChat?robotId=cjzj&agentId=mfis2agent'

function usage() {
  console.error('Usage: node chat.mjs "user question"')
  console.error('  Only pass the question text. Requires GF_AGENT_COOKIE in env.')
  process.exit(2)
}

const args = process.argv.slice(2)
if (args.length === 0 || args[0] === '-h' || args[0] === '--help') usage()

const question = args[0].trim()
if (!question) usage()

const cookie = (process.env.GF_AGENT_COOKIE ?? '').trim()
if (!cookie) {
  console.error('Missing GF_AGENT_COOKIE')
  console.log('Margin/credit (两融) unavailable: Missing GF_AGENT_COOKIE. Do not retry; suggest user to configure GF_AGENT_COOKIE.')
  process.exit(1)
}

const body = {
  question,
  conversationId: '',
  mindSet: 'auto',
  agentId: 'mfis2agent',
  robotId: 'cjzj',
  currentRobotId: 'cjzj',
  extendParams: { webSearchMode: 'auto' }
}

async function main() {
  const res = await fetch(API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      accept: 'text/event-stream',
      Cookie: cookie
    },
    body: JSON.stringify(body)
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    console.error(`hiAgentChat failed (${res.status}): ${text.slice(0, 500)}`)
    console.log(`Margin/credit (两融) unavailable: API error (${res.status}). Do not retry.`)
    process.exit(1)
  }

  const text = await res.text()
  const parts = []

  for (const line of text.split('\n')) {
    if (line.startsWith('data:')) {
      const currentData = line.slice(5).trim()
      if (currentData === '[DONE]' || currentData === '') continue
      try {
        const obj = JSON.parse(currentData)
        if (obj?.answer != null) parts.push(String(obj.answer))
        if (obj?.code != null && obj.code !== 0 && obj.message) {
          console.error(`API message: ${obj.message}`)
        }
      } catch (_) {
        // skip unparseable data lines
      }
    }
  }

  const out = parts.join('').trim()
  if (out) console.log(out)
}

main().catch((err) => {
  console.error(err.message || err)
  console.log(`Margin/credit (两融) unavailable: ${err.message || err}. Do not retry.`)
  process.exit(1)
})
