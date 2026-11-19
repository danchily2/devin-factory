---
name: factory-linear-state
description: Read and update the shared Linear labels, workflow statuses and single durable factory state comment. Required by every factory skill.
---

# Linear is the source of truth

Read this before acting. Use the selected runtime adapter for tool calls. Only pilot teams:
MANM (Manager Mobile App) = `0bab2835-3ed3-4089-bed2-129d6febe92c`;
EMPM (Employee Mobile App) = `e00b3530-814b-434d-8b72-e87c05c32b4f`.
Reject other teams without modifying the issue.

## Labels and workflow

The single-select label group **Factory** has children
`intake`, `triage`, `spec`, `spec-review`, `build`, `review`, `human-review`, `blocked`, `done`, `failed`.
Display names may be `Factory › intake`; resolve label IDs by group and child, not an unqualified name.
Replace only the Factory child; preserve unrelated labels.

The single-select **Factory signal** group has children `approve`, `answered`, `revise`, `stop`.
Only humans add these. The foreman reads and removes them, never adds one. Relays do not consume signals.
Use label/event identity and timestamp when available to distinguish repeated uses of the same signal.
answered supplies a pending question's answer; with no pending question it is a valid nudge/resume at any
nonterminal stage, not approval. Any human signal may wake/resume a verified finished/unreachable owner;
only the foreman applies stage-specific semantics. A nudge never bypasses unanswered questions or gates.

Never add workflow states. Existing states are Backlog, Todo, In Progress, In Review, Done, Canceled, Duplicate.
Map triage/spec/spec-review to Todo; build to In Progress; review/human-review to In Review;
done to Done. Intake/blocked/failed leave workflow status unchanged. On stop, set Factory to failed,
leave status unchanged, and comment exactly the reason `stopped by human`. Do not change status to Canceled.
An externally Canceled or Duplicate issue must not be built or merged; ask for human direction.

## One durable comment

Use get_issue plus **all pages** of list_comments. Locate the one body beginning exactly
`<!-- factory-state -->`. Create it only if none exists; otherwise update with save_comment **with its id**.
Foremen resolve multiple matching comments with the claim tie-break below; relays block and report.
Invalid JSON or unsupported versions are a blocking integrity error: report to a human; do not guess or
overwrite. The body is the marker then a fenced JSON block, e.g.:

<!-- factory-state -->
```json
{
  "version": 1,
  "issue": "MANM-123",
  "foreman": "SESSION-ID",
  "stage": "triage",
  "size": null,
  "repos": [],
  "children": {"triage": null, "spec": null, "build": null, "review": null},
  "spec_doc": null,
  "pr": {},
  "review_rounds": 0,
  "last_signal": null,
  "updated_at": "2026-01-01T00:00:00Z"
}
```

This is the exact field set in schemas/state.json. size is null or S/M/L; repos are canonical
owner/repo strings. spec_doc is a Linear document URL or null. pr maps each routed repo to its PR URL
(empty before PRs). children are runtime handles, null until started. foreman is the current owner handle.
last_signal is null or {name, event_id, received_at}; event_id may be null if unavailable.
updated_at is UTC RFC3339. Never store secrets or full tool output here.

## Transition protocol

After creating a state comment, re-read all comment pages BEFORE posting anything else or dispatching children.
Apply the same claim tie-break when resuming and before every side effect: the earliest-created state comment
wins (sort by createdAt ascending, then comment id ascending for equal timestamps). Track the comment id
you created or resumed; never switch comments to evade a losing claim. If your state comment
is not the earliest, delete only your own state comment, cancel only children you started, cancel your own
reminders, post nothing else and end your own session. Never mark the issue failed or touch the winner's
state, labels or children. Devin uses the supported end/terminate operation; Claude finishes silently.
The winner never deletes another foreman's comment; wait for losing claims to clean up before dispatch.
Unknown comment ownership or a duplicate that cannot self-clean requires human resolution, not extra children.

Only the current foreman writes state. Before any side effect re-read ownership, stage and signals.
If another live foreman owns it, hand off and exit. A fresh foreman may claim only after the old owner
is verified finished/unreachable, not merely waiting. Re-read after claiming; on a race yield to the
already active owner. The API has no compare-and-swap: ownership is best-effort; ambiguous concurrent
claims require human resolution, never duplicate builds.

On every transition update this same comment, label, mapped status and updated_at. Linear writes are not
atomic: re-read and repair label/status from the state comment after partial failure before dispatch.
Check existing children, documents and PRs before retrying a side effect; never duplicate on a timeout.
Persist each child handle and artifact immediately, even when stage is unchanged.
Write human-readable questions, resume stage, event receipts and failure reasons in separate ordinary comments.

For a signal, record last_signal and the intended action in state/an ordinary comment before removing the
signal label with save_issue (preserving all other labels). Then perform that action idempotently.
On resume reconcile the recorded action against artifacts; do not replay completed work.
Same-event duplicates are ignored; a new event with the same signal name is not a duplicate.
If event IDs are missing, correlate the active label with a timestamp/receipt; ambiguity blocks action.

## Output contract

Return the validated schemas/state.json object plus the state comment id to the caller.
Do not add the comment id to the JSON state. Non-foremen return proposed transitions, never write state.
On tool failure report the operation and recovery needed; do not claim the transition succeeded.
