# Devin runtime adapter

Load the plugin before running these prompts. Skills are policy; this file maps their runtime verbs.
Use native Linear and GitHub integrations, not this repo's Claude .mcp.json.

## Foreman and stage sessions

- Spawn a stage with **devin_session_create**, passing the matching skill invocation, issue key,
  state comment id, scope/approved spec, repository gates, parent handle and concrete budget in its prompt.
  Set **notify_on_response=true** and **structured_output_schema** to the parsed object from
  schemas/triage.json, spec.json, build.json or review.json (not a filename string).
- Tag every child `factory` and `factory:<ISSUE-KEY>`; tag the foreman likewise.
  Set a child ACU limit no higher than the remaining approved run budget.
- Persist the returned session handle immediately. On a response notification, retrieve the result using
  **devin_session_interact** (read/status/events operation as exposed by the current tool) and validate the
  structured output before transitioning. Never use a child saying "done" as a substitute for the schema.
- Use **devin_session_interact** with a message to the EXISTING build child for every revision.
  Likewise message existing spec/review children for revisions/re-review; do not start a second stage session.
  Include new heads, findings and human instructions and request the same output contract.
- Use **devin_session_interact** to query foreman liveness and to deliver relay events.
  Waiting/sleeping sessions are live. On stop use its supported cancel/terminate operation for running
  children; verify cancellation, report failures and do not authorize further writes.
- While awaiting humans use **devin_reminder_manage** to schedule a wake-up in two hours with issue key
  and state comment id; re-arm after re-reading state if still waiting. Cancel the reminder on progression,
  stop or completion. Prefer response notifications over timers for child completion.
- On done/failed (including stop), first persist terminal state, close/cancel children and cancel reminders.
  Post a final short summary comment, then explicitly end the foreman's OWN session using the supported
  end/terminate operation via **devin_session_interact** or host equivalent. Inspect its live schema;
  do not invent an operation or merely wait idle. Never end before terminal persistence succeeds.
  Later relay/intake events on done/failed are no-ops unless a human authorizes a new run.

Tool schemas can differ by host release. Inspect each live tool's schema before supplying operation names,
budget/tag fields or reminder payloads; the bold tool names and required behaviors above are fixed.
If a capability is unavailable, report the missing capability and block instead of inventing a successful call.
No Devin integration is invoked merely by installing the plugin.

## Linear native MCP

Use the Linear MCP operations named **get_issue**, **list_comments**, **save_comment**, **save_document**,
and **save_issue** (the host may namespace them).
- get_issue: fetch the issue with labels/team/status and attachments.
- list_comments: exhaust pagination and locate the marker comment.
- save_comment: create only on first intake; pass **id** to update the same comment on every transition.
- save_document: pass **issue** to attach the spec; use the existing document id when revising.
- save_issue: resolve label IDs and existing workflow state IDs, preserve unrelated labels,
  replace only the Factory child, remove only a consumed Factory signal, and set mapped status.

Use available read/search MCP tools to resolve labels, documents and workflow states. Do not create states.
GitHub native read/check/merge operations establish actual PR heads, required checks and merge truth.
Repository branch protection is authoritative.

## Automation deployment

The automations directory contains JSON **drafts**, not installed automations. Inspect the current
**devin_automation_manage** schema, translate condition/action syntax if necessary, substitute all
PLACEHOLDER values and review budgets/network policy before create/update. Keep disabled until verified
against sample events from both teams. No live automation tool was available when authoring these drafts.
Authentication and permissions must already be provisioned; never put access tokens in plugin files.
