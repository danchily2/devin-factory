# Claude Code runtime adapter

Start with `claude --plugin-dir /path/to/devin-factory`. Connect the Linear and GitHub remote MCP servers
from .mcp.json and authenticate interactively through Claude's MCP authentication flow. Devin instead uses
its native integrations. Do not hard-code tokens; GitHub server access may depend on account policy.

## Stage mapping

The foreman is the current long-lived Claude conversation, not a new Task for each transition.
Run stages via **Task** subagents using agents/triage.md, spec.md, build.md and review.md.
Provide the matching skill, issue/state id, approved scope, repo roots and parsed schemas/<stage>.json;
request ONLY schema-conforming JSON and validate before accepting it.

For each repository create a dedicated git worktree on `factory/<issue-key-lowercase>-<slug>` for
the build stage. First inspect existing worktrees/branches: reuse the run's worktree on resume, never
overwrite someone's checkout. Give triage/spec read-only access; review independently reads the build
worktree/diff without edits. Do not let multiple writers share a worktree.

Store each returned Task/resume id in state.children. Resume that SAME Task for build revisions and
spec/review follow-ups, using the host's Task resume feature. If Task resume is unavailable, block for
human recovery; do not silently start another writer. Return the same schemas as Devin.
Use the conversation/resume handle as state.foreman; do not invent a Devin session id.

Android validation on a host without Android/KVM is manual: ask the operator for a Linux/device runner
against the exact PR head, reuse that validation context on revisions, and collect the spec's build/on-device
results and screenshot attachment URLs in the PR and build result. Do not invent platform: linux Task
support or Devin child handles. Missing, empty or stale evidence remains blocked; review reports a human item.

## Linear and wake-up differences

Call the Linear MCP get_issue, list_comments, save_comment (with id on updates), save_document
(with issue attachment) and save_issue using the same state skill. Read all pages and preserve labels.
Use GitHub MCP for PR/check/merge truth and repo-local git for diffs/worktrees.

Devin automations, session tags/ACU, reminders and cloud session liveness are NOT Claude Code capabilities.
For a local Claude run, a human reopens/resumes the foreman conversation to relay approve/answered/revise/stop
or merged PRs; it re-reads Linear before acting. Record this manual wake requirement at every checkpoint.
There is no unattended two-hour reminder guarantee here: use an explicitly configured external scheduler
to resume it every two hours, or human wake-ups. The watchdog can be invoked manually in a separate
conversation, but cannot declare another conversation dead without an operator verifying it.
Do not claim parity with cloud relay scheduling when no scheduler is configured.

Checkpoints, max two review rounds, stop behavior, schemas, branch rules and merge restrictions are identical.
Cancel active Tasks on stop with the host's supported mechanism; if unavailable notify the operator,
halt dispatch and withhold all merge authorization.

## Output

Each Task returns the matching stage schema. The foreman persists state.json and reports next human action.
On done/failed (including stop), first persist terminal state, close/cancel Tasks and cancel any configured
reminders. Post a final short summary comment, then finish the conversation with a final report; do not wait
idle. Never finish before terminal persistence succeeds. Later relay/intake events are no-ops unless a
human authorizes a new run.
Host errors/missing resume handles are blocked recovery, never successful completion.
