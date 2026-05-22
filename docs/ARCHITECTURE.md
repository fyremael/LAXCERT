# Architecture: LAXFORGE ↔ LAXCERT

## 1. System boundary

```text
┌─────────────────────────────────────────────────────────────────────┐
│                            LAXFORGE                                 │
│  ansatz_forge → curvature_solver → gauge_reducer → prior_art_matcher │
│          ↓                                                          │
│  proof_emitter / certificate_exporter                               │
└──────────┬──────────────────────────────────────────────────────────┘
           │ candidate.json + normalized AST + proof strategy
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            LAXCERT                                  │
│  schema validator → Lean emitter → lake build → proof-status.json    │
└──────────┬──────────────────────────────────────────────────────────┘
           │ proof result + logs + hashes
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                             AETHER                                  │
│  append-only provenance, proof status, gauge class, assumptions      │
└──────────┬──────────────────────────────────────────────────────────┘
           │ certified operator artifact
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            MODULUS                                  │
│  geometric/operator interpretation, downstream architecture use      │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Candidate lifecycle

1. LAXFORGE generates an ansatz.
2. LAXFORGE solves coefficient constraints.
3. LAXFORGE normalizes the result in Python/SymPy.
4. LAXFORGE emits an AST-based certificate.
5. LAXCERT validates schema.
6. LAXCERT emits Lean.
7. `lake build` checks the generated theorem.
8. LAXCERT emits proof status.
9. AETHER records candidate lineage and proof result.
10. LAXFORGE updates ranking, novelty, and rejection state.

## 3. Artifact hashing

Every build should record:

- candidate JSON hash;
- normalized JSON hash;
- emitted Lean hash;
- LAXFORGE git SHA;
- LAXCERT git SHA;
- Lean toolchain string;
- mathlib revision;
- CI run id;
- proof status.

The proof result is valid only for this exact artifact tuple.

## 4. The right failure taxonomy

A failed build does not simply mean "bad candidate." It can mean:

- unsupported syntax;
- malformed certificate;
- missing assumption;
- failed type elaboration;
- nonzero residual;
- gauge transform ill-typed;
- proof search insufficient;
- Lean/mathlib version drift.

The proof-status format must preserve this distinction.
