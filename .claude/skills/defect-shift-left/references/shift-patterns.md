# Common Shift Patterns

Recurring moves that shift a defect class from a later stage to an earlier
one, with the recipe, tooling, and completion condition of each. `SKILL.md`
§6 names them; this file carries how to apply them. Section numbers match the
stub, so a §6.x reference resolves in either file.

### 6.1 Untyped → strict-typed source

|            |                                                                                       |
| ---------- | ------------------------------------------------------------------------------------- |
| **Shifts** | Type errors, null deref, registry-shape drift, silent `undefined` from bracket access |
| **From**   | Stage 6+ (unit test) or Stage 10 (production)                                         |
| **To**     | Stage 0 (type system)                                                                 |

Convert source to a language with a checking compiler (JS → TS, Python → typed
Python under `mypy`/`pyright`, Ruby → RBS/Sorbet). Then progressively enable the
strictest flags — `strict`, `noUncheckedIndexedAccess`, `strictNullChecks` — and
retire every `@ts-nocheck` / `# type: ignore` escape hatch. Each flag flip is
its own shift: the compiler enumerates the defects, you fix them in batches.

The shift completes only when the strict typecheck is a **blocking gate** at
both pre-commit (fast feedback on staged files) and CI (full-repo backstop). A
typecheck nobody runs is theatre — see §6.4.

### 6.2 ADR → executable architectural rule

|            |                                                                                               |
| ---------- | --------------------------------------------------------------------------------------------- |
| **Shifts** | Forbidden imports, layering violations, banned API usage, accidental cross-subsystem coupling |
| **From**   | Stage 1 (design doc) or Stage 7+ (code review)                                                |
| **To**     | Stage 2 (editor rule) + Stage 5 (blocking static analysis)                                    |

Architectural rules expressed in prose are advice; rules expressed in lint
config are enforcement. `eslint-plugin-boundaries`,
`import/no-restricted-paths`, `dependency-cruiser`, ArchUnit (JVM), and
`import-linter` (Python) — all turn an ADR sentence into editor feedback and a
build failure.

The recipe: encode each architectural decision as a rule that fails the build
when violated. The ADR document remains as rationale; the lint config is the
enforcement.

For the encoding pattern see `architecture-as-code`, with concrete
implementations in `architecture-as-code-javascript` or
`architecture-as-code-python`. For first principles see
`architecture-guidelines`; for the topology rationale this enforces, see
`morphogenetic-architecture`.

### 6.3 Hand-validated boundary → schema-as-code

|            |                                                                                                            |
| ---------- | ---------------------------------------------------------------------------------------------------------- |
| **Shifts** | Config drift, API contract mismatch, malformed input, doc-vs-reality skew                                  |
| **From**   | Stage 6+ (hand-rolled `if`-chain validators) or Stage 10 (runtime parse errors, prose-as-contract)         |
| **To**     | Stage 0 (codegen), Stage 2 (editor), Stage 5 (build), Stage 8a (deploy) — **one artifact, multiple rungs** |

Schemas are the highest-leverage shift in this catalogue because the same
artifact powers checks at every stage that can read it:

- **Stage 0** — codegen produces static types: JSON Schema →
  `json-schema-to-typescript`; OpenAPI → server / client stubs; Protobuf → typed
  clients; XSD → C# / Java classes.
- **Stage 2** — editor schemas drive autocomplete and inline validation for
  hand-edited files (`$schema` in JSON, `xsi:schemaLocation` in XML, YAML
  language server hints).
- **Stage 5** — CI validates committed files against the schema (`ajv`,
  `xmllint`, `spectral` for OpenAPI, `buf lint` for Protobuf).
- **Stage 8a** — pre-deploy gate rejects config that does not match the schema
  before it reaches a running service.
- **Boundary runtime** — schema-bridged TS libraries (`zod`, `typebox`, `io-ts`,
  `valibot`) make the schema the single source: static type plus runtime
  validator generated from one declaration. Use at every external input
  boundary (HTTP body, env vars, message payload).

Catalogue: JSON Schema (configs, `package.json`), OpenAPI (HTTP), gRPC /
Protobuf (service-to-service), GraphQL SDL, AsyncAPI (events), Avro (streaming),
XSD (XML / SOAP).

The win is not _"we validate"_ — it is _"validation comes from a single artifact
that fans out to every appropriate stage."_ Two hand-written sources checking
the same shape are the same-scope duplication §Directive 3 forbids; one schema
is the antidote.

### 6.4 Optional check → blocking gate

|            |                                                 |
| ---------- | ----------------------------------------------- |
| **Shifts** | The check itself, from advisory to enforced     |
| **From**   | Stage where the check exists but does not block |
| **To**     | Same stage, now a gate                          |

The most common shift-left failure is having the right check at the right stage
and not making it block. A typecheck run as a manual `npm run` command has zero
shift-left value relative to no typecheck at all. Audit:

- Pre-commit hook fails → does it block the commit, or just print?
- CI job fails → does branch protection require it before merge?
- Lint warning → is the rule severity `error` or `warn`?
- Coverage drop → does it fail the build, or land in a report nobody opens?

### 6.5 Scope-justified backstops

§Directive 3 allows later backstops when two layers run the same check on
different scopes:

- **Pre-commit** — staged files only, fast, narrow, bypassable with
  `--no-verify`.
- **CI** — full repo, slow, complete, un-bypassable behind branch protection.

Both are warranted: different blast radii (single commit vs. branch), different
bypass costs. Layering pays when the earlier layer is faster _and_ bypassable —
the later layer is the un-bypassable backstop, not a duplicate.

### 6.6 Hand-checked aspect coverage → fitness function

|            |                                                                                  |
| ---------- | -------------------------------------------------------------------------------- |
| **Shifts** | Aspect coverage gap: a subsystem in an aspect's governed set lacks the mechanism |
| **From**   | Stage 7+ (code review, incident)                                                 |
| **To**     | Stage 5 (fitness function in blocking static analysis)                           |

An aspect's obligation holds across a declared set of subsystems. A dependency
rule can confine its mechanism (§6.2) but cannot require that every governed
subsystem reaches it; a fitness function can. Its population is the subsystem
registry `architecture-as-code` assembles, its assertion is the oracle
`test-strategy` §7 defines for the aspect, and its runner is the stack's
fitness-function tool — `dependency-cruiser` `required` rules, ArchUnit, or a
grimp-based test. This skill places the check; it does not design the oracle.
