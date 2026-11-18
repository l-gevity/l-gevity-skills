# Push-out: move recurring work into durable systems

Push-out reduces operational work that depends on people remembering or executing steps. Use it when the same question, ticket, manual procedure, or dependency on one teammate keeps returning.

## Core concepts

Recurring work can live at six levels:

```mermaid
flowchart LR
    A["0: Memory"] --> B["1: Runbook"] --> C["2: Repo script"]
    C --> D["3: Shared platform"] --> E["4: Self-service"] --> F["5: Feedback"]
```

Execution moves; responsibility stays with a named owner. Choose the level justified by frequency, risk, and reach. A rare task may need only a reliable procedure.

## Apply it

1. Check whether the task still needs doing. Delete unnecessary work before standardizing it.
2. Make the procedure explicit and verify it works. Automate the repeatable steps, then share them when several teams have the same need.
3. Add self-service only with validation, scoped permissions, policy, auditability, and recovery. Add feedback when a measured threshold can drive a useful response.

Once executable configuration owns the mechanics, documentation keeps the purpose, owner, unusual constraints, and recovery guidance. Link to the implementation instead of maintaining a second description of every step.

## Project example

Certificate rotation depends on one engineer. First capture and verify the procedure. Then use a maintained renewal job with validation and failure notification. A broader platform is warranted only if several teams need the same capability. Prove the replacement works before retiring the manual path.

> `$push-out` Reduce our manual certificate-rotation work. Identify its current home and the smallest durable next step, with ownership and recovery.

[Full skill](../.claude/skills/push-out/SKILL.md)

<!-- skill-revision: e55a9a254a1d -->
