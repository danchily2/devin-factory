---
name: factory-review
description: Independently review factory PRs against the issue and approved spec, returning structured findings without editing or merging.
---

# Review stage

1. Read factory-linear-state, factory-repo-gates and the runtime adapter. Independently fetch issue,
   approved spec (or S/no-spec acceptance criteria), all routed PR diffs and current head SHAs.
   Do not rely on the builder's summary as evidence.
2. Inspect correctness, scope, acceptance criteria, regression/security risks, tests and required checks.
   Verify claimed behavior in code and results. Include normal/empty/error cases. Record any visual
   verification not performed. Do not edit code or merge.
   For Android code, verify build and spec on-device results, exact PR head SHA and accessible screenshot
   attachment URLs from the Linux Android child (or capable Linux host/manual Claude validation).
   Missing, empty, inaccessible or stale Android evidence is a human item, never accept; an APK or green
   JS checks alone do not prove runtime behavior. Check the evidence independently, not just its verdict.
3. Rank findings blocker/high/medium/low with repository, file/line evidence, impact and concrete fix.
   An unavailable diff, missing PR, unknown head or missing gate is not acceptance.
4. Return accept only with no unresolved findings requiring changes and all gate evidence verified;
   revise for actionable implementation defects; human for decisions, inaccessible evidence or risks
   requiring human judgment. An empty diff without justified evidence is human, not automatic accept.
5. On a re-review message reuse this review stage session but independently fetch new heads/diffs.
   The foreman caps completed review rounds at two; do not dispatch more work yourself.

## Output contract

Return ONLY schemas/review.json JSON. Include reviewed_heads for every repository, verdict, summary,
findings and checks. accept requires no blocker/high findings. Report missing evidence as human findings.
The foreman decides the transition; you do not write Factory labels or state.
