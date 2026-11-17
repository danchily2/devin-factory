---
name: factory-build
description: Implement one approved factory issue on factory branches, return tested PRs, and revise in the same stage session.
---

# Build stage

1. Read factory-linear-state, factory-repo-gates, the runtime adapter, issue, triage acceptance criteria and
   approved spec document (unless the foreman explicitly records the S/no-spec decision).
   Check current ownership, stage and stop before writes. Never self-approve a spec.
2. Work in isolated checkouts/worktrees for all routed repos. Read local guidance. Reuse the existing
   factory branch/PR; use the prescribed branch and PR naming and link Linear in every PR body.
3. Implement the agreed scope only, add normal/empty/error coverage, run targeted tests and required repo
   gates once inputs settle. For user-facing work capture requested UI evidence; explicitly report
   visually unverified surfaces. Never substitute a build result for a visual check.
4. Push and open/update PRs. Return commands, results, evidence and blockers without hiding failing gates.
   Do not merge at this stage. The foreman will dispatch independent review and a human checkpoint.
5. When messaged with revisions, continue in THIS build session and its branches, not a new session.
   Re-read issue/spec, apply findings, retest changed inputs and update the same PRs. Return the same contract.
   If the session is lost, block and ask for recovery authorization rather than silently creating a second builder.
6. Only on a later explicit foreman merge authorization may this same child merge Android under every
   factory-repo-gates condition. Never merge iOS/vmm. Check stop and head/check status immediately beforehand.

## Output contract

Return ONLY schemas/build.json JSON, including all PRs and per-repo checks/evidence.
ready means all routed repos have a PR and local gates pass; pending GitHub checks remain recorded, not passed.
blocked/failed identifies missing permissions, failing checks or unresolved decisions in blockers.
Empty scope is blocked, not a no-op PR. A merge response uses the same contract with actual PR status.
