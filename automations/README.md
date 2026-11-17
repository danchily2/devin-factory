# Deployment drafts, not active automations

A1–A4 are disabled inputs shaped around devin_automation_manage's event/schedule -> start_session model.
No automations were installed or tested against live event delivery. The authoring environment did not
expose devin_automation_manage, so field nesting, condition operators and event-template binding must be
confirmed against its current schema. Do not submit these blindly.

1. Inspect the live manage tool schema and sample Linear/GitHub event envelopes.
2. Replace every PLACEHOLDER (integration ids, event expression, network domains); translate condition
   syntax and session_settings/limits/net_policy placement if required. Never insert tokens.
3. Confirm whether addedLabel.name is the leaf name or qualified display name. The drafts use leaf
   intake/approve/answered/revise/stop; adjust only to real payload names, keep group verification in skills.
   Confirm data.teamId, pull_request.head.ref, action and merged payload paths before enabling.
4. Validate team filters against MANM and EMPM ids; test that another team/label group does NOT start work.
   A1 targets intake only; A2 targets all four human signals. A3 resolves team from the recorded issue.
5. Review budgets: A1 150 ACU, A2/A3 5, A4 10. These are suggested ceilings, not an org budget approval.
   Include git-manager.devin.ai in the network allow policy plus only necessary service/build domains.
6. A1 and relay sessions bypass approval so they can spawn/message without stalling. A2/A3 and A4 use Lite.
   The start prompt must receive the actual event envelope, not the literal placeholder.
7. Dry-run duplicates, live owner, finished owner, stop, all-PR merge and stale scan before enabling.
   Configure any integration-specific concurrency limit to avoid parallel intake owners.
8. Enable via devin_automation_manage only after operator review. Record deployment IDs outside this repo
   if sensitive. A4 is hourly UTC; waiting foremen also use a two-hour reminder.
