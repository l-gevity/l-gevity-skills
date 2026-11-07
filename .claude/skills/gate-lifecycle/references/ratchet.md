# Ratchet and Expiry Encodings

Two small, encoding-neutral algorithms. Write each in the project's own language
and keep it pure over its inputs, so its unit tests are the gate's negative
control.

## Reconcile

Inputs: `baseline` and `observed` map each entry to its value, the second measured
from the current tree. `named` is the set of entries this change explicitly
accepts. For an exception list the value is presence; for a size or count baseline
it is the number.

```text
refused, accepted, shrunk = {}, {}, {}
for entry, value in observed:
    if entry not in baseline or value > baseline[entry]:
        if entry in named: accepted[entry] = value
        else:              refused[entry] = value
    else if value < baseline[entry]:
        shrunk[entry] = value
stale = entries in baseline and not in observed

if refused is not empty:
    fail the gate; write nothing
next = baseline - stale + shrunk + accepted
```

| Output | Meaning | Action |
| --- | --- | --- |
| `refused` | New violation or growth nobody named | Fail the gate. A red run writes nothing. |
| `accepted` | Growth this change names | Write it; the change's message carries the entry and the reason |
| `shrunk` | Debt paid down | Lower the entry with no decision |
| `stale` | Entry no longer violates | Remove it, or fail until it is removed |

- `named` is per entry, as in `--accept-growth <path>`. A flag that accepts
  everything is the regeneration this algorithm replaces.
- Either stale policy ratchets: removing the entry automatically, or failing until
  someone does. Keeping it does not, because the next regression fits under it.
- Test `reconcile` on all four outputs. The refused case is the negative control.
- A hand-maintained list with no tool follows the same rule in review: a diff that
  adds an entry and names nothing is rejected.

## Dated Expiry Step

A suspension is data, not a comment, so a step can read it. Each entry holds the
gate, the criterion, the owner, and the expiry.

```text
for suspension in suspensions:
    if today > suspension.expires:
        fail "<gate> suspended until <expires>, owner <owner>,
              criterion <criterion>: decide REINSTATE, RETIRE, or renew on measured data"
```

- Run the step on every change and on a schedule. An expiry fires with no commit
  to attach it to, so a step that runs only on changes can wait forever.
- A renewal changes the date and cites the data measured in the window that ended.
  The step cannot tell a renewal from a moved date; review of that change can.
- The strongest form lapses on its own: the skip condition tests the date, so the
  gate runs again at expiry with nobody acting. Prefer it where the gate can carry
  the date, and keep the step for suspensions that live in configuration.
