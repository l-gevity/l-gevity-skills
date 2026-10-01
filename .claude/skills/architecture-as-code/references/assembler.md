# Architecture as Code — The Assembler

Reference for [SKILL.md](../SKILL.md) §5. Read before building, adapting, or
debugging an assembler or the rule block it emits. Writing or changing a
per-subsystem architecture file needs only SKILL.md §§1–4.

## 5. The assembler

A small script invoked at lint time (CI / pre-commit / editor). Concept is
identical across stacks; encoding is not.

```
# 1. Discover — recursive walk, skipping the configured ignore-list
#    (vendor / build / cache / virtualenv dirs).
files = walk(REPO_ROOT, name = "<config-filename>")
files.sort(by_depth, descending = True)   # deeper-first

# 2. Concat. `components` is the deprecated alias for `subsystems`: warn on
#    it, treat it as `subsystems`, and reject a file that carries both.
subsystems = []
forbidden  = []
for f in files:
    data = parse(f)
    subsystems.extend(data.subsystems ?? data.components)
    forbidden.extend(data.forbidden)

# 3. Expand wildcards against the live registry.
#    Turn a spec ('foo' | 'foo-*' | '*' | list | parametric) into
#    a concrete list of subsystem names, with `except` subtracted.
#    Fail when a spec or `except` resolves to no registered subsystem, or a
#    subsystem pattern matches no file: an unknown name expands to an empty
#    set and drops its rule while lint stays green.
names = [c.name for c in subsystems]
def expand(spec, except_):
    if spec is parametric: return spec     # passthrough
    types = resolve_to_names(spec, names)  # handles *, prefix-*, lists
    if except_: types = types - resolve_to_names(except_, names)
    return types

# 4. Emit the stack's native lint config from `subsystems` + expanded `forbidden`.
#    4a. Forward EVERY field the subsystem schema defines — name, pattern,
#        mode / single, capture. A field the emitter drops is unexpressible in
#        every architecture file in the repo; `mode` is the usual casualty, and
#        it is the one the repository root needs (Directive 6).
#    4b. Scope the emitted rule block to the ENTIRE linted source set — never a
#        subdirectory allowlist (Directive 7).
#    4c. Emit the file-existence rule ("every file matches a declared
#        subsystem") at error severity alongside the dependency rules
#        (Directive 8).

# 5. Invoke the stack's lint tool against the emitted config.
```

The discovery + merge + wildcard-expansion pipeline is the same everywhere.
Steps 4 and 5 are the only stack-specific parts.

> [!NOTE] The generated lint config is a **build artifact** — git-ignored,
> regenerated on every run. The source of truth is the per-subsystem
> architecture files.
