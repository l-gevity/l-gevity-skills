# Quality Model Sweep

Companion to `requirements-grounding` workflow step 9. Use it to find
obligations the sources imply but never state. It lists characteristics, not
requirements: a characteristic becomes a requirement candidate only when an
actor, source, or evidence supports it.

## How to sweep

1. Walk every characteristic below against the problem scope.
2. Record one of three states per characteristic:
   - `covered` — name the requirement slugs that carry it;
   - `not applicable` — state the reason in one line;
   - `open` — name the owner and the question; do not invent a target.
3. Treat an `open` security, safety, reliability, or inclusivity-related
   characteristic on a must-have scope as a risk finding in the decision
   record.
4. Prefer an authoritative basis (law, contract, standard, policy) for
   security, safety, accessibility, and compliance characteristics; those
   obligations do not wait for a product-value experiment.

A candidate set that names no quality characteristic is a coverage finding,
not evidence that none apply.

## Product quality characteristics (ISO/IEC 25010:2023)

| Characteristic | Sub-characteristics | Typical unstated obligation |
| --- | --- | --- |
| Functional suitability | completeness, correctness, appropriateness | Variants and edge cases the source assumes |
| Performance efficiency | time behaviour, resource utilization, capacity | Response, throughput, and volume limits nobody wrote down |
| Compatibility | co-existence, interoperability | Sharing a host or exchanging data with named systems |
| Interaction capability | appropriateness recognizability, learnability, operability, user error protection, user engagement, inclusivity, user assistance, self-descriptiveness | Accessibility and error-recovery expectations |
| Reliability | faultlessness, availability, fault tolerance, recoverability | Uptime, degraded modes, restore points and objectives |
| Security | confidentiality, integrity, non-repudiation, accountability, authenticity, resistance | Who may see or change what, and what must be provable afterwards |
| Maintainability | modularity, reusability, analysability, modifiability, testability | Change and diagnosis expectations over the product's life |
| Flexibility | adaptability, scalability, installability, replaceability | Growth, new environments, and replacement of parts |
| Safety | operational constraint, risk identification, fail safe, hazard warning, safe integration | Harm to people, property, or environment when the system misbehaves |

Mapping from ISO/IEC 25010:2011. Renamed: usability to interaction
capability, portability to flexibility, accessibility to inclusivity, user
interface aesthetics to user engagement, maturity to faultlessness. Added:
safety as a whole characteristic, plus the user assistance,
self-descriptiveness, resistance, and scalability sub-characteristics. A
project profile that still uses the 2011 names may keep them; record the
mapping once in the legend.

## Quality in use

Effectiveness, efficiency, satisfaction, freedom from risk, and context
coverage describe outcomes of real use, not properties of the product. They
belong to outcome hypotheses (see `## Outcome Hypothesis Shape` in the skill),
measured after representative use, and are outside this sweep. The
quality-in-use model moved to ISO/IEC 25019:2023.

## Guardrails

The skill's guardrails govern what may become a requirement; this reference
adds only sweep mechanics.

- Close an `open` characteristic by recording the measurement it needs, never
  by supplying a target the sources do not carry.
- Do not let a project taxonomy that omits a characteristic silence it; mark
  it `open` and route the question to the taxonomy owner.
