---
# Rendered by alchemy-orchestrate scripts/init_workspace.py from envelopes.implementer in alchemy-workspace.json.
name: alchemy-implementer
description: {{ envelopes.implementer.description | quote }}
maxTurns: {{ envelopes.implementer.budget.max_turns }}
tools: Read, Grep, Glob, Edit, Write, Bash, Skill
disallowedTools: Agent
isolation: worktree
---

{{ envelopes.implementer.instructions }}

Load each skill with the Skill tool. When the Skill tool does not offer a skill, read `SKILL.md` in that skill's directory under {{ skills.roots | code_list }}, then the references it links that your package needs.
