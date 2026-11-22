# Enforcement Handoffs — Worked Records

Read when `architecture-guidelines` §10 hands a principle to
`architecture-as-code`, or records that it yields no handoff. Each record names
the principle, the constraint it implies, and the rule to encode or the reason
none applies.

```
Principle:   interface discipline
Constraint:  external callers use the facade only
Enforcement: add architecture rule: forbid * -> <subsystem-internal-*>, except <subsystem-*>
```

```
Principle:   integration discipline
Constraint:  no subsystem reaches a peer application's internals
Enforcement: add architecture rule: forbid * -> <peer-storage-client | peer-internal-*>, except <integration-adapter-*>
```

```
Principle:   aspect extraction
Constraint:  only <audit-mechanism> reaches the audit internals and SDK
Enforcement: add architecture rule: forbid * -> <audit-internal-*>, except <audit-mechanism>
```

A principle that settles as no handoff:

```
Principle:   layer self-sufficiency
Constraint:  the control holds with the layer below absent
Enforcement: none - not an import or dependency edge; verify by exercising the
             subsystem without that layer (`defect-shift-left`)
```

An aspect's coverage obligation, the second handoff beside its exclusivity edge:

```
Principle:   aspect coverage
Constraint:  every subsystem in <holds across> routes through <audit-mechanism>
Enforcement: none - not an edge; place a coverage check over the subsystem
             registry (`defect-shift-left`)
```
