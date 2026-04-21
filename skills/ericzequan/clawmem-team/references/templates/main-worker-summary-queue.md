# Main Worker Summary Queue Template

Use this reference when a user wants the current ClawMem Team demo shape moved out of the plugin and into an external template.

## Best fit

Use this template when:
- one agent should coordinate
- a worker pool should execute
- work should be visible in a shared queue repo
- task status should advance through an explicit label protocol

## Participant readiness

Before using this template, confirm the current OpenClaw environment already has:
- the ClawMem plugin installed and enabled
- the bundled `clawmem` runtime skill available to the participating agents

Use this template with a default starting topology of:
- 1 main agent
- 2 worker agents

Treat fewer than 3 participating agents as not ready for this template. If the user wants a smaller setup, switch to a custom Team design instead of silently shrinking this template.

For each selected participant, track these readiness layers:
- OpenClaw status: `existing`, `to-create`, or `user-confirmed only`
- ClawMem status: `configured`, `bootstrap-on-first-use`, or `blocked`
- runtime delegation status: `verified`, `not-yet-tested`, `session-refresh-required`, or `blocked`

Only treat a participant as ready when that agent can use ClawMem in the current OpenClaw host.
Only treat the template as fully ready when the main control path can actually dispatch to the required workers.

## Agent selection flow

- If only the current agent is known:
  1. Explain that this template expects `1 main + 2 workers`.
  2. Confirm the new worker agents will also run in the same OpenClaw environment with ClawMem available.
  3. If the runtime can create agents, prepare two worker agents after explicit user approval.
  4. Otherwise stop at a readiness plan and ask the user to create or expose the missing workers.
- If multiple agents already exist:
  1. Inspect or confirm the available agents.
  2. Filter out any agents that cannot use ClawMem in the current host.
  3. Ask whether to use the default 3-agent topology or to choose specific existing agents.
  4. If the user has no strong preference, keep the current agent as `main` and choose two existing agents as workers.

## Post-bootstrap session readiness

If setup changes the OpenClaw agent list, worker workspaces, gateway config, or pairing state:
- assume the current session may no longer be a valid worker-dispatch path
- require a fresh session or repaired pairing before claiming the template is fully ready
- report `partial` instead of `ready` until one real worker handoff succeeds

If multiple OpenClaw agents share one ClawMem backend identity:
- disclose that repo authorship and comments may still appear under one shared backend account
- do not use shared authorship alone as proof that different workers actually acted

## Recommended protocol

This template may use a protocol like:
- `queue:task`
- `task-status:todo`
- `task-status:handling`
- `task-status:blocked`
- `task-status:done`
- `assignee:<agent-id>`

These labels belong to this template, not to the ClawMem plugin.

## Recommended blueprint shape

Define:
- one main agent
- two worker agents by default
- one shared summary queue repo
- optional extra workers or private/project repos for deeper execution work when the user already operates a larger pool

## Bootstrap path

1. Inspect or confirm the available agents.
2. Confirm the current OpenClaw environment has ClawMem enabled for the participating agents.
3. Reconcile the current inventory with the required `1 main + 2 workers` shape.
4. Prepare missing worker agents if the runtime supports it and the user approves it.
5. Confirm which agents will act as `main` and `workers`.
6. If agent config or gateway state changed, record whether the current session needs refresh before worker verification.
7. Confirm the org boundary and who owns the queue repo.
8. Create or reuse the summary queue repo.
9. Create or reuse the team and grants.
10. Write the template contract into the canonical Team artifact.
11. Seed one queue issue to prove the flow works.

## Demo flow

One minimal demo should show:
1. main agent creates a queue task
2. one worker agent receives a real handoff through a working dispatch path
3. that worker agent starts work and adds a progress comment
4. that worker agent posts the result
5. queue status moves to `task-status:done`
6. the second worker agent can at least see the queue repo and task labels

The main agent writing queue comments on behalf of a worker does not prove the Team works.
If dispatch fails because the current session needs refresh, pairing repair, or another runtime fix, the result is `partial`, not `ready`.
