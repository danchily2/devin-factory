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

## Linux Android child

For routed vmm android/ or scarlet-team-c-android on macOS or without accessible /dev/kvm, the build child
uses **devin_session_create** with **platform: "linux"**, the same repo, **notify_on_response=true**, tags
`factory` and `factory:<ISSUE-KEY>`, and a budget within the approved build/run remainder. Create ONE child
for that repo, not a second implementation writer. Inspect the live schema for repo/limit field names.
Prompt it to fetch the exact PR head SHA in a detached checkout, verify KVM, run repo Android build gates
and every spec on-device case, and attach screenshots. No source edits, commits, pushes or merge authority.
Set **structured_output_schema** to this parsed JSON object:

```json
{
  "type": "object", "additionalProperties": false,
  "required": ["result", "checks", "evidence"],
  "properties": {
    "result": {"type": "string", "enum": ["passed", "failed", "unavailable"]},
    "checks": {"type": "array", "items": {
      "type": "object", "additionalProperties": false,
      "required": ["command", "result", "head_sha", "evidence"],
      "properties": {
        "command": {"type": "string", "minLength": 1},
        "result": {"type": "string", "enum": ["passed", "failed", "unavailable"]},
        "head_sha": {"type": "string", "minLength": 1},
        "evidence": {"type": "string", "minLength": 1}
      }
    }},
    "evidence": {"type": "array", "items": {"type": "string", "format": "uri"}}
  },
  "allOf": [{
    "if": {"properties": {"result": {"const": "passed"}}},
    "then": {"properties": {
      "checks": {"minItems": 1, "items": {"properties": {"result": {"const": "passed"}}}},
      "evidence": {"minItems": 1}
    }}
  }]
}
```

Persist its handle/repo/head in the build session and PR body, not a new state.children key. Use
**devin_session_interact** to reuse the same Android child on revisions and to retrieve/validate results;
never infer completion from a notification. Reject results for another head and non-attachment evidence
URLs; verify all spec cases are covered. Missing/empty evidence or tooling failure is blocked/failed,
not passed. Map checks to schemas/build.json checks (put head SHA in each evidence string), screenshot
URLs to evidence, and failure/unavailable details to blockers; also record the child result in the PR body
and build summary. A capable Linux build host may run the checks itself with the same head/evidence gates.
Propagate stop/terminal cleanup to the Android child. If its parent is lost, the foreman uses the recorded
handle to cancel it; require recovery authorization before replacing a lost child. Claude validation is manual.

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

A2/A3 use **message_session** with **auto_create: true**, one standing Lite dispatcher per automation.
Each event re-reads Linear, relays to the foreman and returns to waiting; signals do not spawn new relays.
For a stuck nonterminal issue, a human adds Factory signal › answered (or any human signal): A2 messages
the live owner or starts a fresh foreman from state when the owner is verified finished/unreachable.
answered with no pending question is a nudge/resume, not approval. Uncertain liveness or missing state
blocks recovery; terminal done/failed stays a no-op. Foreman human-facing checkpoint/status comments include:
"Stuck for a few hours? Add Factory signal › answered to nudge."

The automations directory contains JSON **drafts**, not installed automations. Inspect the current
**devin_automation_manage** schema, translate condition/action syntax if necessary, substitute all
PLACEHOLDER values and review budgets/network policy before create/update. Keep disabled until verified
against sample events (A1/A2 allow MANM only). No live automation tool was available when authoring these drafts.
Authentication and permissions must already be provisioned; never put access tokens in plugin files.
