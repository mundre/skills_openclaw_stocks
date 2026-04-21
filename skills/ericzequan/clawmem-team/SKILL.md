---
name: clawmem-team
description: Single entry skill for ClawMem Team workflows. Use when a user wants to design, bootstrap, verify, adapt, or choose a Team workflow on top of ClawMem, including custom Team design, repo and access planning, main/worker/summary queue setups, reviewing flows, step-by-step Team onboarding, or direct template requests by filename such as main-worker-summary-queue.md and reviewing.md.
---

# ClawMem Team

Use this skill as the single entry point for ClawMem Team requests.

Keep the product boundary explicit:
- ClawMem plugin provides memory and atomic collaboration tools.
- This skill defines how those primitives are composed into a Team workflow.

## Available templates

- `main-worker-summary-queue.md`
  - Best for one coordinating agent plus worker agents.
  - Recommended starting shape is `1 main agent + 2 worker agents`.
  - Use when work should move through a shared queue repo with explicit task labels and status changes.
  - If the user names this template directly, read `references/templates/main-worker-summary-queue.md`.
- `reviewing.md`
  - Best for code review, PR review, design review, architecture review, or document inspection.
  - Use when review work needs a clear requester, reviewer set, artifact location, and completion rule.
  - If the user names this template directly, read `references/templates/reviewing.md`.

Users may refer to a template by filename, for example:
- "Based on `main-worker-summary-queue.md`, set up my team"
- "Based on `reviewing.md`, set up my team"

## Select the right path

1. Confirm the user wants Team design, Team setup, Team verification, or a Team template.
2. If this is only an ordinary memory request, stay on the bundled `clawmem` skill instead.
3. Choose one of three paths:
   - explicit template: the user directly names a file under `references/templates/`
   - matched template: the user's request clearly fits one of the available templates
   - `custom`: no template clearly fits, so design a Team from scratch

## Template readiness

Before producing a blueprint for a multi-agent template, confirm these readiness layers:
- environment readiness: the current OpenClaw host has ClawMem installed and enabled, and the bundled `clawmem` runtime skill is available
- participant inventory: which OpenClaw agents already exist and which ones still must be prepared
- ClawMem readiness: whether each selected agent is already configured, will bootstrap on first use, or is blocked
- runtime delegation readiness: whether the current control session can still dispatch real work to the required workers, or whether session refresh / pairing repair is still required

For `main-worker-summary-queue.md`:
- treat `1 main + 2 workers` as the default minimum ready shape for this template
- do not treat a selected participant as ready until that agent can use the ClawMem runtime in the current OpenClaw environment
- if only the current agent is available, prepare two worker agents first when the runtime exposes agent-creation capability and the user approves it
- if the runtime cannot list or create agents, stop at a readiness plan and ask the user to confirm or prepare the missing agents
- if multiple agents already exist, ask whether to use the default 3-agent shape or to choose specific existing agents
- if the user has no stronger preference, keep the current agent as `main` and assign two workers
- if bootstrap changes the OpenClaw agent topology, gateway state, or pairing state, assume the current session may need refresh before worker dispatch can be verified
- do not report this template as `ready` until one real worker handoff succeeds through a working dispatch path instead of only by config inspection or main-authored proxy writes

## Read the right reference

- For any Team blueprint, read [references/blueprint.md](references/blueprint.md).
- For Team bootstrap and mutation sequencing, read [references/bootstrap.md](references/bootstrap.md).
- For readiness checks and end-to-end proof, read [references/verification.md](references/verification.md).
- For the main/worker/summary queue template, read [references/templates/main-worker-summary-queue.md](references/templates/main-worker-summary-queue.md).
- For the reviewing template, read [references/templates/reviewing.md](references/templates/reviewing.md).

## Workflow

1. Identify the user's goal, constraints, participants, and preferred collaboration style.
2. If the user directly names a template file, use that template first.
3. Otherwise, choose a template when it clearly fits. If no template clearly fits, design a custom Team.
4. Inspect or confirm the participant readiness required by the selected template or custom design.
5. If the chosen path needs multiple agents, decide whether to reuse existing agents or prepare missing ones before bootstrap.
6. Produce one explicit Team blueprint using `references/blueprint.md`, even when starting from a template.
7. Keep the Team contract explicit in the blueprint:
   - roles
   - repos
   - access model
   - issue or comment protocol
   - canonical Team artifact
   - verification path
   - environment readiness state
   - participant readiness state
   - runtime delegation readiness state
8. If the user approves actual changes, bootstrap the Team using `references/bootstrap.md`.
9. If bootstrap changed agent config, restarted the gateway, or otherwise invalidated the current control path, refresh or re-establish the session before end-to-end worker verification.
10. When the Team is configured, verify it using `references/verification.md`.
11. If the user wants a demo, seed only one minimal workflow object.

## Decision rules

- If the user explicitly names a template file, prefer that template unless it clearly conflicts with the request.
- Prefer a matched template when the user asks for a common Team shape.
- Prefer custom design when the user describes a unique workflow, org boundary, or access model.
- Do not assume the current host can list or create OpenClaw agents. Use those capabilities only when the runtime exposes them.
- For templates with a minimum participant shape, stop at readiness planning when the required agents are still missing.
- If several agents are already available for `main-worker-summary-queue.md`, ask whether to use the default 3-agent shape or a user-selected subset.
- If a selected agent lacks ClawMem configuration but can bootstrap on first use, record that state in the blueprint instead of treating it as a blocker.
- If the current session cannot dispatch to the required workers after bootstrap, report `partial` or `blocked` instead of `ready`.
- Do not treat main-authored proxy comments, config inference, or shared-identity authorship alone as proof that a worker actually executed the task.
- If bootstrap changes agent config or restarts the gateway, expect a fresh session or repaired pairing before claiming end-to-end success.
- Ask for clarification only when the goal, participants, or execution model is still ambiguous after the first pass.
- Do not invent a hidden Team protocol inside the plugin. If a protocol is needed, make it explicit in the blueprint or template output.
- Do not refer to other sibling skills. This single skill owns the full Team journey.
- Keep one canonical Team artifact. Do not scatter the Team contract across multiple uncoordinated files or issues.
- Use ClawMem collaboration tools first. Use shell or raw API only when the required operation is not exposed by tools.
- Require explicit approval before writes that create agents or change orgs, teams, invites, memberships, or permissions.
- Do not let a template bypass blueprint, bootstrap, or verification. Templates guide the design; the Team still must be made explicit and verified.

## Required output

Before ending any major phase, summarize:
- chosen path
- why that path fits
- environment readiness state
- participant readiness state
- runtime delegation readiness state
- the blueprint or mutation plan
- the next concrete step
