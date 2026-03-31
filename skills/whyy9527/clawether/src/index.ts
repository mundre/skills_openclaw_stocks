import { definePluginEntry } from 'openclaw/plugin-sdk/core'
import { createPluginRuntimeStore } from 'openclaw/plugin-sdk/runtime-store'
import { Type } from '@sinclair/typebox'

const ENDPOINT = process.env.CLAWETHER_ENDPOINT ?? 'https://clawaether.com'

// ─── Runtime store: persists agent_token within this OpenClaw session ─────────
const store = createPluginRuntimeStore<{ agentToken: string | null }>({
  agentToken: process.env.CLAWETHER_AGENT_TOKEN ?? null,
})

async function api(path: string, method = 'GET', body?: unknown) {
  const token = store.get('agentToken')
  const res = await fetch(`${ENDPOINT}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }))
    throw new Error(err.error ?? 'API error')
  }
  return res.json()
}

function cellToText(value: unknown): string {
  if (value === 0 || value === null || value === undefined || value === '') return '.'
  if (value === 1) return 'B'
  if (value === 2) return 'W'
  return String(value)
}

function renderBoard(board: unknown): string {
  if (!Array.isArray(board)) return String(board ?? '')
  return board
    .map((row) => Array.isArray(row)
      ? row.map((v) => cellToText(v).padStart(5)).join(' ')
      : cellToText(row)
    )
    .join('\n')
}

function formatLegalMoves(moves: unknown): string {
  if (!Array.isArray(moves)) return 'none'
  if (moves.length === 0) return 'none'
  if (moves.length <= 8) return moves.join(', ')
  return `${moves.slice(0, 8).join(', ')} ... (${moves.length} total)`
}

// ─── Plugin ───────────────────────────────────────────────────────────────────

export default definePluginEntry({
  id: 'clawether',
  name: 'ClawAether',

  register(sdk) {
    // ── new_session ──────────────────────────────────────────────────────────
    sdk.registerTool({
      name: 'clawether_new_session',
      description:
        'Start a new ClawAether game session. On first call, the server auto-issues an agent token that is stored for this session. Supports multiple games via game_id.',
      parameters: Type.Object({
        model: Type.Optional(Type.String({ description: 'Your model ID, e.g. claude-opus-4-6' })),
        game_id: Type.Optional(Type.String({ description: 'Game to play, e.g. 2048 or gomoku' })),
      }),
      async execute(_id, params) {
        const agentId = process.env.CLAWETHER_AGENT_ID ?? 'openclaw-agent'
        const data = await api('/api/v1/sessions', 'POST', {
          agent_id: agentId,
          model: params.model ?? 'openclaw',
          game_id: params.game_id ?? '2048',
        })

        // Auto-save the server-issued token (only on first call or if changed)
        if (data.agent_token && data.agent_token !== store.get('agentToken')) {
          store.set('agentToken', data.agent_token)
        }

        return {
          content: [{
            type: 'text',
            text: [
              `Game: ${data.game_id ?? params.game_id ?? '2048'}  |  Session: ${data.session_id}  |  Token: ${data.agent_token}`,
              `Score: ${data.score}  |  Status: ${data.status}  |  Legal moves: ${formatLegalMoves(data.legal_moves)}`,
              '',
              renderBoard(data.board),
            ].join('\n'),
          }],
        }
      },
    })

    // ── move ─────────────────────────────────────────────────────────────────
    sdk.registerTool({
      name: 'clawether_move',
      description:
        'Make an action in a ClawAether session. Keep calling until status is terminal.',
      parameters: Type.Object({
        session_id: Type.String(),
        action: Type.Optional(Type.String({ description: 'Generic action string, e.g. left or 7,7' })),
        direction: Type.Optional(Type.Union([
          Type.Literal('up'), Type.Literal('down'),
          Type.Literal('left'), Type.Literal('right'),
        ])),
      }),
      async execute(_id, params) {
        const action = params.action ?? params.direction
        if (!action) {
          throw new Error('action is required')
        }
        const data = await api(
          `/api/v1/sessions/${params.session_id}/move`,
          'POST',
          { action }
        )

        const lines = [
          `${String(action).toUpperCase()}  │  score: ${data.score} (+${data.gained ?? 0})  │  moves: ${data.move_count}  │  max: ${data.max_tile}  │  ${data.status}`,
        ]
        if (data.status === 'running') lines.push(`Legal: ${formatLegalMoves(data.legal_moves)}`)
        else if (data.status === 'win') lines.push('Game won.')
        else if (data.status === 'draw') lines.push('Game ended in a draw.')
        else lines.push('Game over.')
        lines.push('', renderBoard(data.board))

        return { content: [{ type: 'text', text: lines.join('\n') }] }
      },
    })

    // ── get_state ────────────────────────────────────────────────────────────
    sdk.registerTool({
      name: 'clawether_get_state',
      description: 'Get current state of a ClawAether session.',
      parameters: Type.Object({ session_id: Type.String() }),
      async execute(_id, params) {
        const data = await api(`/api/v1/sessions/${params.session_id}`)
        return {
          content: [{
            type: 'text',
            text: [
              `Game: ${data.game_id ?? 'unknown'}  │  Session: ${data.session_id}  │  score: ${data.score}  │  ${data.status}`,
              `Legal: ${formatLegalMoves(data.legal_moves)}`,
              '',
              renderBoard(data.board),
            ].join('\n'),
          }],
        }
      },
    })

    // ── leaderboard ──────────────────────────────────────────────────────────
    sdk.registerTool({
      name: 'clawether_leaderboard',
      description: 'View the ClawAether global leaderboard, optionally filtered by game.',
      parameters: Type.Object({
        game_id: Type.Optional(Type.String({ description: 'Optional game filter, e.g. 2048 or gomoku' })),
      }),
      async execute(_id, params) {
        const query = params.game_id ? `?game_id=${encodeURIComponent(params.game_id)}` : ''
        const data = await api(`/api/v1/sessions${query}`)
        const rows = data
          .slice(0, 10)
          .map((r: { agent_id: string; model: string; score: number; max_tile: number; game_id?: string }, i: number) =>
            `${String(i + 1).padStart(2)}. [${r.game_id ?? params.game_id ?? '2048'}] ${r.agent_id} (${r.model})  —  ${r.score.toLocaleString()} pts  max:${r.max_tile}`
          )
          .join('\n')
        const title = params.game_id ? `ClawAether Leaderboard (${params.game_id})` : 'ClawAether Leaderboard'
        return { content: [{ type: 'text', text: `${title}\n\n${rows}` }] }
      },
    })
  },
})
