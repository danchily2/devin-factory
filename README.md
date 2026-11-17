# Devin Factory

A Linear-driven software factory for Devin and Claude Code. Add a label to a pilot issue and one long-lived
**foreman** carries it from triage to PR, delegating to isolated triage, spec, build and review children.
Linear labels and one durable state comment make the run resumable without duplicating builders.

This is a plugin of skills and contracts, not a background service. Installation does not modify Linear
or deploy automations. Version **0.1.0**, Apache-2.0, by Dan-Mihai Cuc <dan-mihai.cuc@visma.com>.

## Install

You need access to this private repository, the target repos, Linear, and GitHub.

### Devin

```sh
devin plugins install danchily2/devin-factory
# Or from a local clone:
devin plugins install --local /path/to/devin-factory
```

Devin loads the Claude plugin layout. In cloud, make this repository's skills available through your
organization's plugin/skill installation and invoke `@skills:factory-foreman` with the issue key.
Confirm all nine skills are visible before enabling automations. Devin uses its **native integrations**,
not .mcp.json. It needs session create/interact, reminders, Linear and GitHub permissions.
See [runtime/devin.md](runtime/devin.md) for exact tool mapping.

### Claude Code

```sh
git clone https://github.com/danchily2/devin-factory.git
claude --plugin-dir ./devin-factory
```

This loads the plugin locally without requiring a marketplace. The root .mcp.json declares remote
Linear (`https://mcp.linear.app/mcp`) and GitHub (`https://api.githubcopilot.com/mcp/`) servers.
Review/enable the servers and authenticate using Claude's MCP authentication flow; do not put tokens
in the repository. GitHub remote access depends on your account/organization policy.
Ask Claude to run factory-foreman for e.g. MANM-123. Stages are resumable Task subagents in isolated
git worktrees. Human/scheduled wake-ups are manual unless you configure an external scheduler;
Devin's cloud automations are not installed for Claude. See [runtime/claude.md](runtime/claude.md).

## Linear setup (operator action)

Pilot teams only:

| Key | Team | ID |
| --- | --- | --- |
| MANM | Manager Mobile App | 0bab2835-3ed3-4089-bed2-129d6febe92c |
| EMPM | Employee Mobile App | e00b3530-814b-434d-8b72-e87c05c32b4f |

Create or verify these **single-select label groups**, scoped/available to both teams:

- **Factory**: intake, triage, spec, spec-review, build, review, human-review, blocked, done, failed.
- **Factory signal** (humans only): approve, answered, revise, stop.

For example the UI displays `Factory › intake`; integrations may deliver the leaf name `intake`.
Resolve group/label IDs and verify event payloads before enabling drafts. Do not create workflow states:
use the existing Backlog, Todo, In Progress, In Review, Done, Canceled, Duplicate states.

| Factory stage | Existing workflow status |
| --- | --- |
| triage / spec / spec-review | Todo |
| build | In Progress |
| review / human-review | In Review |
| done | Done |
| intake / blocked / failed (including stop) | Leave unchanged |

The foreman maintains ONE comment starting `<!-- factory-state -->` then a fenced JSON block.
It records owner, stage, child handles, spec document, per-repo PR URLs, review count and signal receipt.
Do not manually duplicate/delete it. Full shape: [schemas/state.json](schemas/state.json) and
[factory-linear-state](skills/factory-linear-state/SKILL.md).

## Start and steer

1. Add **Factory › intake** to a MANM/EMPM issue with a clear outcome and acceptance criteria.
   A1 starts a foreman for MANM (invoke it manually for EMPM or until automations are deployed).
2. Triage chooses repositories, size S/M/L and whether a spec is needed. Only S with needs_spec=false
   skips spec. Questions cause blocked; answer in a comment then add **Factory signal › answered**.
3. A spec is a **Linear Document attached to the issue**, never a spec PR.
   At spec-review read it and add **approve** or comment concrete changes and add **revise**.
   A revised spec requires a new approval.
4. Build opens linked PRs; independent review can request changes from the **same** build child.
   At most two completed review rounds run; remaining findings escalate to human-review.
5. Every run pauses at **human-review**. Humans merge iOS/vmm. Android build child may auto-merge after
   human approve only when independent review accepts current heads and all required checks, including
   **ui-smoke**, pass. This conservative approve gate preserves the human checkpoint.
   Comment feedback + **revise** reuses the existing builder; after the review cap, humans must merge.
6. Add **stop** at any time to cancel children, set Factory failed with reason **stopped by human**,
   and leave workflow status unchanged. Foreman reads then removes signals; it never adds them.
7. Once all recorded PRs are verified merged, the foreman marks Factory done / workflow Done.
   A closed-unmerged PR is not completion.

Signals are stage-specific: approve at spec-review/human-review, answered at blocked, revise at
spec-review/human-review; invalid-stage signals are explained and removed, not treated as approval.
If an issue is Canceled/Duplicate or state ownership is ambiguous, work blocks for human direction.
For a failed/done run request explicit operator recovery/new-run authorization; re-adding intake does not
silently erase prior history. Tool failures and missing child handles are surfaced, not papered over.

## Repository policy

- MANM: Visma-Manager/vmm (React Native) and/or either scarlet repository.
- EMPM: Visma-Mobile-Employee/scarlet-team-c (iOS) and/or scarlet-team-c-android (Android).
- iOS and vmm: **never automatically merged**.
- Android: build child may auto-merge only under the gates above and branch protection.
- Branch: `factory/<issue-key-lowercase>-<slug>`; PR title starts with the issue key; body links Linear.
- Multi-repo runs keep a PR URL for each repo and wait for **all** merges before Done.

Exact commands/required checks are discovered from each target repo, not guessed by this plugin.

## Automations and waiting

[automations/](automations/) contains **disabled JSON drafts**, shaped for devin_automation_manage:

| Draft | Trigger | Session |
| --- | --- | --- |
| A1 | linear:label_added intake, MANM only | foreman |
| A2 | linear:label_added approve/answered/revise/stop, MANM only | standing Lite dispatcher |
| A3 | github:pull_request closed+merged, head begins factory/ | standing Lite dispatcher |
| A4 | hourly UTC, nonterminal Factory state stale >6h | Lite watchdog |

A2/A3 use message_session with auto_create: true, one dispatcher per automation, re-reading Linear for
each event and returning to waiting. EMPM remains supported by skills but is not opted into A1/A2 drafts.
Relays message the owner from the state comment; only a verified gone/finished owner is replaced with
a fresh foreman that resumes state. Waiting is not dead. The foreman also arms a two-hour reminder
while waiting on a human, and children notify their parent on response.

**Before deployment:** inspect the current devin_automation_manage schema, replace every PLACEHOLDER,
validate real payload paths/label names and condition syntax, review ACU ceilings/network allow policy
(including git-manager.devin.ai), test duplicates and recovery, then explicitly enable.
The authoring environment did not expose the automation API; these are not live API-validated exports.
See [automations/README.md](automations/README.md). No production setup was performed.

## Skills and contracts

| Skill | Purpose |
| --- | --- |
| [factory-foreman](skills/factory-foreman/SKILL.md) | Durable issue owner and checkpoints |
| [factory-relay](skills/factory-relay/SKILL.md) | Signal/merge wake-up and safe owner recovery |
| [factory-watchdog](skills/factory-watchdog/SKILL.md) | Stale-state scan and nudges |
| [factory-triage](skills/factory-triage/SKILL.md) | Size, scope, questions, spec decision |
| [factory-spec](skills/factory-spec/SKILL.md) | Attached Linear Document spec |
| [factory-build](skills/factory-build/SKILL.md) | Implementation, gates and PRs |
| [factory-review](skills/factory-review/SKILL.md) | Independent findings and verdict |
| [factory-linear-state](skills/factory-linear-state/SKILL.md) | Labels, statuses and exact state contract |
| [factory-repo-gates](skills/factory-repo-gates/SKILL.md) | Routing, tests and merge authority |

Draft-07 JSON schemas live in schemas/. Runtime callers must also check semantics that need external
facts: routed repos equal PR/check coverage, no duplicate per-repo entries, issue/team routing, ready
results satisfy gates, reviewed heads match current heads, and every PR is merged before done.
The stdlib validator checks repository structure/JSON/frontmatter/references, **not** JSON Schema
meta-validation, payload validation, live MCP availability or end-to-end orchestration.

## Validate locally

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Python 3.9+; no third-party packages. CI runs both commands. Tests cover valid, empty and broken fixtures.
Design and state diagram: [docs/DESIGN.md](docs/DESIGN.md). Release notes: [CHANGELOG.md](CHANGELOG.md).
