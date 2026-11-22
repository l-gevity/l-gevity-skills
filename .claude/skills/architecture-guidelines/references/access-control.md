# Access Control — Granting, Delegating, and Revoking Rights

Read when §8 sends you here: a change lets one actor give, delegate, transfer,
or remove another actor's rights — invitations, sharing, roles, ownership
transfer, provisioning from an identity provider, API keys, service accounts —
or decides which records a request may read or change. §8 owns that each layer
checks access itself; this file owns what a correct grant is. `infrastructure-fit`
owns the identity-provider choice.

## 1. Grant rules
| Rule | Statement | Typical defect |
|:--|:--|:--|
| Attenuation | A grant never exceeds what the grantor holds: no role, scope, resource, or duration beyond the grantor's own | An editor invites an owner; an admin of one workspace grants rights in another |
| Re-check at acceptance | A pending grant or invitation re-checks the grantor's rights when accepted, not only when sent | A removed member's invitations still admit people |
| Last owner | A resource that needs an owner always keeps one; the removal, demotion, or departure that would leave none is rejected by a conditional write on one record every such change writes — the resource's owner count or version — or by a serializable transaction (`concurrency-control`); a condition on the member row alone admits write skew, and a count read beforehand is a race | Two owners demote each other at once |
| Revocation | Removing a right removes what derives from it — delegated grants, open invitations, sessions and tokens issued under it — within a declared bound | A revoked user's API key keeps working |
| Denial writes nothing | A denied request, a provisioning call included, leaves no record, partial account, or pending row; only the audit entry | A rejected provisioning call leaves a disabled user that later blocks the real one |
| Scope from grants | A request may name a tenant, product, or resource; the caller's grants decide whether it may act there, and every query is filtered to the granted scope | Changing a tenant ID in the URL reads another tenant's records |
| Cross-site writes | A state change authenticated by ambient credentials proves it came from the application: same-site cookies, an origin check, or an anti-forgery token | A form on another site changes a user's settings |

## 2. Personal-data rights
Access and erasure cover every store that holds the person's data. Keep a store
register: each database, cache, search index, projection, log, analytics sink,
backup, and third-party processor that receives personal data, with its erasure
path and its bound. An erasure that touches only the primary database is
incomplete; a store missing from the register is a defect in the register.
A store that cannot erase in place declares the retention that ends the data.

## 3. Verification
- One generative property over the grant model: for random actors, roles, and
  grant sequences, no reachable state gives an actor a right that no grant chain
  from an owner justifies, and every resource that needs an owner has one. Keep
  the access decision a pure function of grants and request (§3 Functional
  Core) so the property runs at stage 6 without the store.
- One negative test per rule in §1: the forbidden request is denied **and the
  store is unchanged**; assert that no write happened, not only the status.
- Last owner also needs the interleaving test from `concurrency-control`: two
  owners demoting each other concurrently against the real store.
- `test-strategy` chooses fidelity; `defect-shift-left` places the checks
  (authorization model gap: stage 1 threat model, else stage 6 property test).
