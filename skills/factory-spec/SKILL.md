---
name: factory-spec
description: Write or revise a concrete implementation spec as a Linear Document attached to the issue, never as a PR.
---

# Spec stage

1. Read factory-linear-state, factory-repo-gates, the runtime adapter, triage output and issue context.
   Inspect code read-only. Resolve stated questions or return blocked with the missing decisions.
2. Draft scope/non-goals, user behavior, acceptance criteria, affected repositories/files, data/API changes,
   compatibility/migration, security, implementation approach, validation commands and rollout risks.
   Cover normal, empty, loading and failure behavior where applicable. Cite inspected evidence.
3. Use Linear save_document with `issue` set to the issue identifier/id and a clear issue-key title.
   On revision update the existing spec_doc document using its id after resolving its URL; inspect attached
   documents before retrying creation. Do not open a spec PR or write implementation code.
4. Return the document URL and a concise summary for the foreman's spec-review checkpoint.
   Human approval belongs to the foreman, not the spec child.

## Output contract

Return ONLY schemas/spec.json JSON. ready includes a non-null doc_url and no open questions.
blocked/failed includes questions or the actual tool error; missing document creation is not ready.
Empty requirements are blocked. Never claim a document exists without the tool result.
