# Deployment drafts, not active automations

A1 uses start_session. A2/A3 use message_session with auto_create: true: one standing Lite dispatcher
per automation receives events as messages, re-reads Linear per event and waits again instead of ending.
No automations were installed or tested against live event delivery. The authoring environment did not
expose devin_automation_manage, so field nesting, condition operators and event-template binding must be
confirmed against its current schema. Do not submit these blindly.

1. Inspect the live manage tool schema and sample Linear/GitHub event envelopes.
2. Replace every PLACEHOLDER (integration ids, event expression, network domains); translate condition
   syntax and session_settings/limits/net_policy placement if required. Never insert tokens.
3. Confirm whether addedLabel.name is the leaf name or qualified display name. The drafts use leaf
   intake/approve/answered/revise/stop; adjust only to real payload names, keep group verification in skills.
   Confirm data.teamId, pull_request.head.ref, action and merged payload paths before enabling.
4. A1/A2 are MANM-only (0bab2835-3ed3-4089-bed2-129d6febe92c); test that EMPM and other teams/label groups
   do NOT trigger them. A1 targets intake only; A2 targets all four human signals. A3 resolves the pilot
   team from the recorded issue. EMPM remains supported by the skills, not opted into A1/A2 drafts.
5. Review budgets: A1 150 ACU, A2/A3 5. These are suggested ceilings, not an org budget approval.
   Include git-manager.devin.ai in the network allow policy plus only necessary service/build domains.
   A2/A3 ceilings apply to dispatcher sessions, not a fresh allowance per event; review for expected volume.
6. A1 and relay sessions bypass approval so they can spawn/message without stalling. A2/A3 use Lite.
   A2/A3 action is {"type":"message_session","auto_create":true,"prompt":"..."}; creation settings sit
   outside the action. Confirm their live API placement and auto-create permissions before deployment.
   Each action prompt must receive the actual event envelope, not the literal placeholder.
7. Dry-run duplicates, live owner, finished owner, stop, all-PR merge and answered nudges before enabling.
   Configure any integration-specific concurrency limit to avoid parallel intake owners.
   Send multiple issues/events to each dispatcher; verify fresh state reads, error isolation and continued waiting.
8. Enable via devin_automation_manage only after operator review. Record deployment IDs outside this repo
   if sensitive. Waiting foremen still use a two-hour reminder.

Human recovery: add Factory signal › answered to a stuck nonterminal issue. A2 messages a live foreman or
restarts a verified finished/unreachable owner from state; any human signal can wake it, but only answered
with no pending question is a neutral nudge/resume. Signals never bypass their stage/approval rules.
No state means blocked recovery, not intake; done/failed is a no-op without human new-run authorization.
