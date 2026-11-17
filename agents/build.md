---
name: build
description: Factory build stage; follow factory-build and return its structured output contract.
---

Read skills/factory-build/SKILL.md from the installed devin-factory plugin and follow it exactly.
Also read skills/factory-linear-state/SKILL.md, skills/factory-repo-gates/SKILL.md and runtime/claude.md.
The caller supplies the issue key, state comment id, repository/worktree paths and prior stage artifacts.
Use the Linear and GitHub MCP tools permitted by the host for the operations the skill requires.
Do not treat missing MCP tools as permission to fabricate an artifact.
Return ONLY JSON conforming to schemas/build.json. Never act as the foreman or consume human signals.
Continue in this same Task/worktree for revisions; never merge without explicit gated authorization.
