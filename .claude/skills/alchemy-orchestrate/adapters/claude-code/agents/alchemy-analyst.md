---
# Rendered by alchemy-orchestrate scripts/init_workspace.py from envelopes.analyst in alchemy-workspace.json.
name: alchemy-analyst
description: {{ envelopes.analyst.description | quote }}
maxTurns: {{ envelopes.analyst.budget.max_turns }}
tools: Read, Grep, Glob, Bash, Skill
disallowedTools: Edit, Write, NotebookEdit, Agent
---

{{ envelopes.analyst.instructions }}

Load each skill with the Skill tool. When the Skill tool does not offer a skill, read `SKILL.md` in that skill's directory under {{ skills.roots | code_list }}, then the references it links that your package needs.
