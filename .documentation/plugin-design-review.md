# Independent review of plugin design replays

Historical review of the withdrawn behavioral experiment. Active task guidance
has since been restored to the accepted baseline. The recovered inputs and
final metadata are preserved inside `.refactor-evidence/evidence.zip`; original frozen inputs
and raw traces remain in the verified ZIP documented by
[the evidence layout](../.refactor-evidence/README.md).

Review basis: the predeclared rubrics and original source/user-message scope.
The first original-context pair was assessed from its anonymized A/B packet
before looking up the arm assignment. Later incomplete-pair candidate outputs
are reviewed openly; this is not an additional blind model judgment.
No criterion, fixture, guidance, or recorded result was changed by this review.

Historical v5 candidate source SHA-256 (superseded; final v6 below):
`71d97f16db0f1956fd052852b3c96dec8014d07f477dfb75032232e0189309df`.
Original-context fixture SHA-256:
`f1a7adf014af29aa3d021965de9dfb296c095b49599219640bf94164039a2192`.
Original product baseline: `4d1c0a630c5cddb4eb9dbd1e83fa151fd4a73ac4`.

## Reports reviewed

| Scenario / candidate run | Checker words | Report SHA-256 | Status |
| --- | ---: | --- | --- |
| Original context / 1 | 402 | `33f685ff0dd5b4022a19ba57d427b9d031216f6701a9fafdcfaa8185dffd11b9` | Reviewed; ceiling failed |
| Original context / 2 | 524 | `c64e25027628da75f1d2e39a91f13c986795090b75888c5976a5781e4273ce66` | Reviewed; ceiling failed |
| Recovered reduced fixture / 1 | 828 | `01c48dbbaf797f9259537094ff657874e353334613f239578a502b6b5aa98ca6` | Reviewed; ceiling, inventory, free-format failed |
| Recovered reduced fixture / 2 | 1,006 | `8d3942717af5f4039fcc7625e883ce65d3225353e14387a58996644790d091a8` | Reviewed; ceiling, inventory, free-format failed |

The v5 replay was interrupted after these completed candidate outputs.
Original-context pairs 1 and 2 have completed arm reports, but their blind
judge attempts failed with Windows argument-length errors. The reduced
fixture's first before arm also encountered a Windows temporary-directory
cleanup error. These are evaluation errors, not passes. This partial v5
record must not be read as a three-run final pass.

## Concrete findings

Both reviewed reports choose a data catalog over runtime plugin registration,
retain real-network URL/QR presentation, disclose absent schemas/standards and
unrun checks, and keep execution restrictions separate. Neither claims actual
implementation was completed. Those are improvements to the design direction.

Both exceed the predeclared 350-word ceiling, counting dispatch/checkpoint text,
and omit the requested hero acronym row derived from the same supported-format
catalog. That omission matters: the visible supported-currency claim is part
of the originating owner scope, not optional architecture detail.

Run 1 describes free-format as “passthrough” without explicitly marking unknown
formats unverified. It says “two code-distinct URI builders exist,” although
this baseline supplies only the EPC producer (`packages/opap-core/src/sepa.ts`);
template builders are a proposed mechanism, not an observed implementation.
It frames blocked execution policy as an owner decision for real-network QR,
then assumes creation-only presentation. The owner had already excluded
execution and asked for OPID resolution to QR. The report should preserve that
scope and name the technical separation to check instead of presenting a new
product choice as a blocker.

Run 2 calls free-format “validates only and emits no URI/QR” without defining
what unknown-format validation can establish or marking it unverified. Its
currency-width/decimals first action is concrete, but “that one change unblocks
all three” overstates it: URI scheme implementations and separation from
execution policy remain separate obligations. Existing normalization/record
validation and required rail metadata are not explicitly retained in either
short report; they cannot be counted as proven solely from the catalog verdict.

The reduced-fixture run 1 still recommends **four subsystems**, a facade,
check/catalog boundary, coverage fitness function, and new ESLint dependencies.
It defaults to prohibiting saves on an unverified rail, directly losing the
broad free-format behavior. It also says base58check, EIP-55 and IBAN mod-97
rules “exist today”; the fixture supplies only BTC/ETH regexes and no IBAN
implementation. A data-row extension direction alone is therefore not a
minimal-design pass. Its 828-word output also exceeds the unchanged ceiling.

The reduced-fixture run 2 repeats the failure with an explicit four-subsystem
graph and a default curated-only registry. User-declared networks are deferred
behind a new product decision even though this request asks for any currency
or network. Its proposed canonicalization changes the fixture's trim-only
storage behavior; it invents a future payout path and possible AML subsystem
without fixture evidence. The claim that both defects silently lose funds is
too strong for a fixture that stores addresses and does not execute payments.
The 1,006-word output, additional enforcement inventory and deferred custom
path independently fail the unchanged acceptance bar.

## Fixed-source v6 review

Source SHA-256:
`5cac1e7de382a3ef8454bfb21952684bac6c9b4ac59dacb9e87574b5d076e864`.
Both scenario and fixture hashes are unchanged from the predeclared v5 inputs.
Pair 1 was inspected as A/B before consulting its concealed arm key; B is the
candidate. This human inspection is separate from the recorded blind model
judge, which prefers B.

| Scenario / candidate run | Checker words | Report SHA-256 | Status |
| --- | ---: | --- | --- |
| Original context / 1 | 861 | `f1dd14520afba3a5f7e9bc7968005da1873d885f9170a65f83e00f1fcc6a8bfe` | Reviewed; ceiling failed; obligations below remain unproven |
| Original context / 2 | 475 | `e8f809c852b07310e7e9da38028e7d99d14fdf7a823f613cbd47e6f87f55ecc3` | Reviewed openly; ceiling and explicit-route checks failed |
| Original context / 3 | 381 | `7cddb9669a016a4da734deb03eeddcc4dfe8fbbf9918e8ece2c914c0978eb204` | Reviewed openly; ceiling and presentation-boundary checks failed |
| Recovered reduced fixture / 1 | 1,008 | `e7b642db37ee688d3beef44c6bdc335f134dec8d6d75a9b389534cdcc1d22b2e` | Reviewed; ceiling, minimality, free-format failed |
| Recovered reduced fixture / 2 | 1,194 | `adcfeaff6c536b20b667738a7eda1c1cb2f8f0b2414a66ce951254b4edbd3ae1` | Reviewed openly; ceiling and semantic minimality failed |
| Recovered reduced fixture / 3 | 1,141 | `f97a31e6b0c9151db88da78854291ece3821b5c26d31b97b229cc1c7c9f5ca0b` | Reviewed openly; ceiling and semantic minimality failed |

The paired before report is 2,994 words. The candidate is 71% shorter, leads
with a flat catalog and explicitly unverified free-format row, retains a
same-table hero row, and identifies pure presentation outside execution
planning. It names technical separation rather than asking the owner to
re-decide the no-handoff scope. These are concrete improvements. The unchanged
350-word ceiling still fails. A semantic verdict is present (“DROP” the plugin
mechanism; “BUILD-minimal” the catalog). The frozen colon-field checker rejects
`**Decision** —`; the final checker accepts that equivalent explicit verdict.
Both results are preserved separately in the verification summary.

The candidate's lengthy mainnet table goes beyond the observed source. It
lists non-standard XRP URI and other exact schemes without verifying their
supported behavior or clearly reserving those rows behind standards/vectors
checks. The judge notes this same evidence weakness despite preferring B.
No URI is proved invalid by this review, but supported-protocol correctness
is unproven. Network/memo metadata and retention of trim plus existing record
validation are also not explicit enough to demonstrate their obligations.
The hero uses one catalog, but its support claims depend on resolving those
URI gaps. Preference and a smaller average cannot close these checks.

The reduced pair's candidate was also B in its independently anonymized
packet. It retains a facade, `register()`/`freeze()` registry, “CODE plugin”
codec modules and “DATA plugin” network modules, with its own count of seven
added subsystems. It provides no custom/free-format path and states that
nothing is stored unless encoding and checksum verify. The blind judge
prefers A because shorter B loses that obligation. B proposes replacing
trimmed values with canonical addresses and a new stored record shape; it
does not demonstrate preservation of the existing trim-only behavior.

The mechanical inventory check passes this explicit file-tree inventory;
semantic review therefore remains necessary. Its loaded-route check fails
only on `system-optimization`: the frozen parser treats unparenthesized “Y deferred
to iteration 2” as a claim that Y ran. Every actually claimed executed gate
body was loaded. This is an annotation-parser limitation; the recorded check
stays failed in the original artifact. The final checker recognizes the explicit
deferral; this does not rescue independent minimality or ceiling failures.

All three pairs in each v6 scenario are complete. The final source and fixtures
match their saved hashes. The model judge prefers the candidate in two of three
pairs for each scenario; neither scenario passes acceptance. These later open
inspections do not add another blind assessment.

Original-context run 2 improves the direction: one table, the hero derived from
supported rows, and an execution-independent presentation path. It makes the
absent generated schema its first check instead of assuming compatibility.
However, “Free-format = both `null`: any string accepted, no QR” leaves that
custom-input presentation choice unresolved. It acknowledges unverified URI
standards but does not demonstrate preservation of known-format network/memo
metadata and trim. Its actual route appears inline with Dispatch and Companions,
contrary to the separate explicit route field contract, and its 475 words still
fail. The judge's preference does not prove the remaining obligations.

Original-context run 3 is leaner at 381 words but says “Three payload mechanisms
exist” while proposing a universal template for BIP-21/EIP-681/SEP-7. Only the
EPC builder is observed here; the other builders are unverified proposals. It
sends free-format text into QR without explicitly marking it unverified and
requires reversing the production-blocked release policy in the same increment.
That crosses the owner’s presentation-only boundary; presenting real-network
URI/QR must not enable execution. The judge prefers the baseline for those
substantive reasons despite the candidate's lower component count.

Reduced-fixture run 2 still splits the existing function into facade, network
modules and catalog, adds two lint dependencies and a roughly 40-line assembler,
and proposes `{asset, network, value, extras, verified}` plus staged migration.
Its `generic-unverified` module does retain a custom path, but the justification
assumes irreversible transfers the address-storage fixture does not implement.
No failed obligation proves this inventory necessary over a data table within
the existing owner. Known BTC/ETH syntax and trim behavior must be retained;
asserted checksum policy is not evidence that the requested candidate failed.

Reduced-fixture run 3 explicitly ships bitcoin, ethereum, solana and unverified
modules, then rejects two modules because they “break Rule of 3.” This turns a
delay rule into a component quota and invents a third instance. The custom path
is a module with a new 128-character/ASCII restriction; its free-text UI is still
`NOT-READY` pending a product choice. The proposed stored-record rename and
canonicalization are additional changes to the fixture's `{currency, value}`
and trim-only behavior. Registry, lint boundaries and migration remain unforced
even though the keyword inventory checker passes. The judge also identifies
that both arms fail minimality; candidate preference is not a semantic pass.

## Synthetic weekly-email benchmark limitation

The preserved fixtureless `worth-design-minimal-first` recording has no
application fixture. That transcript
returns `NOT-GROUNDED` for absent application evidence and ambiguous free-text
authorship. Output SHA-256:
`ba27d264bd00460a528ef203abc1f413072afeab7328baa6e561fbca50052cbd`.
The blind rubric permits a different verdict supported by scenario evidence,
but the mechanical `preserves-the-worth-verdict` check accepts only
`BUILD-minimal`. The fixture cannot independently justify that single answer.
This was a benchmark contract limitation, not evidence that every blocked
verdict is correct or that the candidate passes. Preserve the failure and do
not loosen criteria after observing it. A grounded synthetic fixture was
subsequently added with its source hashes and rationale recorded before one
new run; request and criteria remained unchanged. Its baseline API checks
pass 5/5, but the new 749-word recording fails 3/9 scenario checks: loaded-route
honesty, explicit list/free-format presentation and the unchanged word ceiling.
See [benchmark correction](benchmark-correction.md). That separate experiment
neither erases the fixtureless failure nor substitutes for the original case.

## What remains unproven

Passing keyword checks is insufficient for format honesty, hero accuracy or
payment URI correctness. Even successful design replays establish behavior
only on these fixtures. The whole original implementation, actual protocol
vectors, runtime no-wallet/no-transaction checks and UI behavior remain
unverified. Judge preference alone cannot override a failed obligation or cap.

The original-context reconstruction includes exact owner messages but omits
preceding assistant replies that gave content to “implement all.” In the raw
session, line 206 listed native EVM, BTC/XBT, XLM, SOL, XMR, ZEC, TON and XNO;
line 304 proposed EVM/BTC/Stellar/Solana first and further XMR/ZEC/TON/XNO/XRP
adapters. The owner later removed payment execution/handoff. These earlier
assistant proposals are recoverable historical material, not accepted design
requirements, but the frozen reconstruction cannot establish preservation of
every named rail or replay the complete conversation. Its inputs are left
unchanged. Do not claim it proves that original “implement all” request fixed.

## Independent semantic checklist for the next fixed-source replay

This is an inspection aid for the existing rubrics, not a changed acceptance
bar. Apply it to each report independently before consulting arm labels or
judge preference. For each item record `pass`, `fail`, or `unclear`, one short
report quotation, and a source/context anchor. `Unclear` is not proof of a pass.
Bind the review to report, source and fixture SHA-256s.

| Item | A passing report shows | Existing obligation |
| --- | --- | --- |
| Catalog and unknown formats | A static data list/table is the NOW shape; broad unknown currency/network input remains possible through a custom/free-format path. No plugin per rail. | Both rubrics: minimal user behavior |
| Custom input honesty | Unknown format is explicitly unverified/custom; syntax checks are distinguished from ownership/payability. It does not promise a universal validator or silently reject uncatalogued formats. | Both rubrics: free-format and truthful validation |
| Normalization and record validation | Existing trim and known-format checks remain in the authoring/record path. Opaque custom input is not blindly lowercased by an EVM-only helper. Missing generated/schema validation is a material unchecked fact when compatibility depends on it. | Original rubric: known-format metadata, trim, existing authoring/record validation |
| Supported URI/QR only | Real-network links and QR are generated for supported schemes with necessary network/memo/amount metadata. Unknown schemes have honest custom/unverified treatment or a named gap. Encoding arbitrary text into QR is not described as protocol verification. | Original rubric: supported protocols; no fabricated universal URI |
| No payment execution | The presentation path cannot launch/connect wallets, submit transactions or unblock execution merely to show real-net QR. Existing unrelated SEPA behavior is preserved unless source evidence warrants changing it. | Original rubric: presentation-only boundary |
| Hero claim | The hero acronym row is retained and derived from the same catalog's actually supported URI/QR entries; it cannot advertise every unknown free-format option as verified support. | Original rubric: accurate catalog-backed hero row |
| Product scope and blockers | User's resolve→review/URI/QR behavior survives. Blockers are evidenced unresolved obligations, not a request to re-decide already stated no-handoff scope or an invented creation-only product. | Original rubric: final scope and evidence-backed verdict |
| Observed versus proposed | Claims about existing builders, schema openness, standards or measured deltas match files read. Proposed builders and unrun checks are explicitly proposals/unverified. | Both rubrics: decisive evidence and material unchecked facts |
| Necessary additions | Each proposed new mechanism repairs a concrete source/user obligation. Gate count does not become component count; registry/loader/extension API remains absent without evidence. | Both rubrics: no unrequired inventories |
| Decision and next action | An evidence-backed verdict and concrete first action are present; that action is not claimed to solve unrelated outstanding obligations. The actual loaded route is explicit. | Both rubrics: verdict, first action, route |
| Review boundary | Original-context report says implementation/tests were not performed. Reduced historical fixture makes no URI/QR implementation claim outside its scope. | Both rubrics: honest coverage |
| Total length | All user-visible report text, including progress/dispatch checkpoints, stays at or below the frozen 350-word checker limit. | Both scenarios: predeclared mechanical ceiling |

Source anchors for the original-context checks: `REPLAY_CONTEXT.md` contains
the owner messages at 13:12, 13:17, 13:19 and 13:45–13:46 UTC;
`apps/browser-payer/ts/userinterface/opid-creator.ts` lines 84–122 contain
existing normalization; `packages/opap-core/src/record.ts` invokes the absent
generated validator; `packages/opap-core/src/sepa.ts` supplies the existing
EPC producer; `apps/browser-payer/ts/userinterface/qr.ts` only encodes its
payload; `reviewed-payment.ts`, the release registry and release-policy tests
separate execution permission from possible presentation. These anchors are
fixture facts, not claims about a newly implemented product.

A compact independent review row can be
`report hash | source hash | checklist item | pass/fail/unclear | quotation | anchor`.
The blind judge needs the rubric plus the reports and only relevant source
snippets for disputed claims; it does not need unrelated full HTML or all skill
bodies. Input-size or runner failures remain evaluation errors, never quality
passes. Judge preference and reduced average length cannot repair an item
that failed.
