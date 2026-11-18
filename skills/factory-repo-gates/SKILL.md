---
name: factory-repo-gates
description: Route MANM and EMPM work to approved repositories and enforce branch, PR, test and merge gates.
---

# Routing and gates

Read factory-linear-state and the issue. Triage chooses only repositories supported by issue scope and
code evidence; do not default every issue to every platform.

| Team | Allowed owner/repo | Platform | Merge authority |
| --- | --- | --- | --- |
| MANM | Visma-Manager/vmm | React Native | Human only |
| MANM, EMPM | Visma-Mobile-Employee/scarlet-team-c | iOS | Human only |
| MANM, EMPM | Visma-Mobile-Employee/scarlet-team-c-android | Android | Build child, under gates below |

For each chosen repository read its contributor guidance, build configuration and required branch checks.
Derive exact local test commands there, not from assumptions about the platform. Record commands, results,
required GitHub checks and UI evidence. Missing tooling, unknown required checks, pending/skipped checks,
or credentials errors are not a pass. Ask a human rather than relaxing protection or editing CI to pass.

Android code includes vmm android/ and scarlet-team-c-android. On macOS or without accessible /dev/kvm,
the build child must delegate to ONE Linux child for the same repo (runtime/devin.md), reuse it on revisions,
and obtain an Android build plus the spec's on-device checks against the exact PR head. Otherwise run
those checks on the capable Linux host. Require per-check commands/results, tested SHA and screenshot
attachment URLs in the PR body and build result. Missing, empty or stale Android evidence is not a pass;
review treats it as a human item. A green JS gate or APK build alone never proves Android runtime behavior.
Claude uses manually arranged Linux/device validation per runtime/claude.md, not fictitious cloud sessions.

Use branch `factory/<issue-key-lowercase>-<slug>` in each repository. PR title starts with the issue key
(e.g. `MANM-123: Fix approval action`). PR body links the Linear issue and spec document if present,
lists acceptance criteria, test results, evidence and known gaps. Reuse the existing issue branch/PR on retry.

Never merge vmm or scarlet iOS. Android may be merged only by the existing build child after the foreman
has posted the human-review checkpoint, received human approve there, and authorized this specific merge.
Require accepted independent review, no unresolved blocking findings, all required checks successful
including `ui-smoke`, approval/branch-protection requirements met, and a fresh stop/signal check.
Enable auto-merge only if protection enforces those requirements; otherwise merge only after observing
all of them pass. Never bypass protection. A failed/missing ui-smoke blocks auto-merge.
No merge of a changed head without rechecking review validity and required checks.
A merged webhook is only a hint: verify the actual PR is merged. Multi-repo work is done only when ALL
recorded PRs are merged; partial merges remain human-review with an explicit progress comment.

## Output contract

Return selected repos with routing evidence, exact gate commands/check names, merge authority and unresolved
gate questions to the stage caller. Triage embeds routing in schemas/triage.json; build embeds checks,
evidence and PR URLs in schemas/build.json. An empty routing decision is blocked, never an implicit default.
