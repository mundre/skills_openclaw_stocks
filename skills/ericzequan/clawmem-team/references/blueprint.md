# Team Blueprint Reference

Use this reference to produce a consistent Team blueprint.

## Goals

The blueprint should:
- be specific enough for bootstrap
- keep conventions explicit
- avoid hiding any Team protocol inside the plugin
- make participant readiness explicit when the Team depends on multiple agents
- be minimal enough that the user can understand and approve it

## Required sections

Return the blueprint with these sections:

### 1. Team Summary

- team name
- target outcome
- why this Team shape fits

### 2. Participants

For each participant include:
- name or agent id
- role
- responsibilities
- whether it is human, agent, or mixed
- OpenClaw status: `existing`, `to-create`, or `user-confirmed only`
- ClawMem status: `configured`, `bootstrap-on-first-use`, or `blocked`

If a template has a minimum participant shape, say whether the current environment already satisfies it.

### 3. Repo Plan

For each repo include:
- repo name
- owner
- purpose
- whether it stores durable memory, workflow coordination, or both
- whether it already exists or must be created

### 4. Access Model

Include:
- organization boundary
- teams to create or reuse
- direct collaborators if any
- repo permissions by actor

### 5. Workflow Contract

Make the operating protocol explicit:
- handoff model
- issue and comment usage
- label or state conventions
- when to create, update, close, or summarize work
- where final outputs land

The plugin does not own this contract. The blueprint does.

### 6. Canonical Artifact

Choose one authoritative place for the Team contract:
- a markdown file
- a bootstrap issue
- a memory node
- another explicit artifact approved by the user

Do not create duplicate sources of truth.

### 7. Bootstrap Plan

List the exact order of work:
1. inspect current participants and existing state
2. prepare missing participants if required and supported by the runtime
3. create missing org / repo / team objects
4. set access
5. materialize the canonical artifact
6. seed the first workflow object if needed

### 8. Verification Plan

Include:
- participant readiness checks
- structural checks
- access checks
- workflow happy-path check
- failure conditions

## Output style

- Prefer short sections over dense prose.
- Use stable names that can be reused during bootstrap.
- If a template inspired the blueprint, say so explicitly.
