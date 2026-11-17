---
name: factory-relay
description: Relay a human Linear signal or a merged factory PR event to the durable foreman, restarting only a finished or unreachable owner.
---

# Short relay

1. Read factory-linear-state and the runtime adapter. Accept the trigger envelope with issue id/key or
   GitHub repository, PR number, head branch, action and merged flag. Missing identifiers -> report and exit.
2. For signals resolve issue and pilot team. For PR events require action=closed, merged=true and head branch
   starting factory/; resolve issue key from branch AND verify the PR is recorded for that issue in state.pr.
   Fetch GitHub truth, do not trust a spoofed or unrelated branch. Unmatched events do nothing.
3. Read all comments, identify and validate the single state comment. No state for a signal/PR event is not
   intake: report missing state; do not silently start a pipeline. done/failed states are no-ops.
4. Check foreman liveness with the runtime. Waiting is live. Message the existing foreman with event identity,
   issue key and a request to re-read Linear/GitHub. On uncertain liveness, do not duplicate it.
5. Only when verified finished/gone, start one fresh factory-foreman with issue and "resume from state";
   require it to recheck ownership. Do not rewrite state ownership yourself.
6. Never consume signals, update Factory state/status, approve, dispatch stages or merge.
   Duplicate events are harmless nudges, not permission to repeat a transition.

## Output contract

Report {issue, action: notified|resumed|ignored|blocked, foreman, reason} as JSON.
No matching input -> ignored; malformed state or inaccessible owner -> blocked with actual error.
Exit promptly; no polling loop. Devin runs this in Lite mode.
