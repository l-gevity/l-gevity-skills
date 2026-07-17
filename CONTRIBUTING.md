# Contributing reusable skill knowledge

This repository is the canonical source for generic skill method. Consumer
projects may prove and refine that method, but they do not become the source of
truth for generic skills.

## Ownership model

- `.agents/skills/` is the canonical editable skill tree in this repository.
- `.claude/skills/` is an exact distribution mirror.
- `.documentation/READ-<skill>.md` explains each skill to human readers.
- Consumer projects pin a reviewed commit or release and keep domain policy in
  project profiles or clearly named project-only skills.

Never fix a generic method only inside a consumer project. Promote the reusable
lesson here first, validate and publish it, then repin the consumer. Never move
project names, private paths, organization roles, product terminology, local
commands, or domain policy into a generic skill.

## Consumer-to-library promotion loop

1. **Capture evidence in the consumer.** Record the failure, correction,
   regression, validator output, or repeated successful pattern.
2. **Identify the generic lesson.** State the behavior that should transfer to a
   second project without importing domain facts.
3. **Choose one owner.** Update the smallest existing skill that owns the method.
   Add a skill only when the capability has a distinct trigger, lifecycle, and
   output contract.
4. **Operationalize first.** Extend validation, fixtures, or output contracts
   before adding broad prose.
5. **Update the complete library bundle.** Keep `.agents` and `.claude` mirrors,
   the matching primer, README index, root guidance, and validator aligned.
6. **Validate in the library.** Run `npm run validate` and inspect the complete
   diff before committing.
7. **Publish, then repin.** Commit/release this repository first. Update the
   consumer's vendored skills and lock to that reviewed revision afterward.
8. **Keep the project overlay.** Local schemas, paths, taxonomies, commands, and
   domain rules remain in the consumer and compose with the generic method.

## Genericity check

A promoted rule must pass all of these:

- It describes a repeatable problem rather than one project's symptom.
- Its vocabulary makes sense without the source project's name or directory
  layout.
- It does not assume a package manager, CI provider, cloud, UI framework, branch
  strategy, or domain taxonomy unless the skill explicitly targets that stack.
- It names the decision owner and the earliest enforceable check.
- Its output contract lets another agent prove whether the method was applied.
- It replaces or tightens an existing rule when possible instead of duplicating
  authority.

## Change checklist

- [ ] Generic skill method changed in `.agents/skills/<name>/SKILL.md`.
- [ ] `.claude/skills/<name>/SKILL.md` is byte-identical.
- [ ] `.documentation/READ-<name>.md` matches the public role.
- [ ] `README.md` indexes new or renamed skills.
- [ ] `CLAUDE.md` and `ALCHEMY-PIPELINE-DESIGN.md` reflect routing changes.
- [ ] `scripts/validate-skills.py` enforces the new invariant where practical.
- [ ] `npm run validate` passes.
- [ ] Consumer project remains domain-specific only and is repinned after
      publication.
