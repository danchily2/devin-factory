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

## Android validation

For vmm android/ or scarlet-team-c-android, check the host before claiming Android coverage.
On macOS or without accessible /dev/kvm, start ONE Linux child for the same repo using the runtime adapter;
do not skip Android or create another build-stage writer. Give it the approved spec and exact PR head SHA
in a detached checkout: run the Android build and the spec's on-device checks, without commits or pushes.
Require the runtime's Android JSON contract: result, checks[] and evidence (screenshot attachment URLs).
Record its handle, repo and tested head immediately in this session and the PR body for recovery/cleanup.
Reuse the same Android child for revisions; send the new PR head and recheck affected spec cases.
Never mark Android checks passed without current-head Android child evidence when delegation is required.
Empty checks/evidence, inaccessible KVM, failed checks or a lost child are blocked/failed with concrete
blockers, never ready; request recovery rather than silently starting a replacement. On a capable Linux
host run those checks locally with the same evidence requirements. Cancel the Android child on stop and
close it at terminal cleanup; keep its handle available to the foreman if this build session is lost.
Before returning, include the child result, tested SHA, per-check results and screenshot attachment URLs
in the PR body and map checks/evidence/blockers into schemas/build.json; do not add new top-level fields.

## Output contract

Return ONLY schemas/build.json JSON, including all PRs and per-repo checks/evidence.
ready means all routed repos have a PR and local gates pass; pending GitHub checks remain recorded, not passed.
blocked/failed identifies missing permissions, failing checks or unresolved decisions in blockers.
Empty scope is blocked, not a no-op PR. A merge response uses the same contract with actual PR status.
