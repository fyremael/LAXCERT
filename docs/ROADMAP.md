# Roadmap

## Phase 0 — Repository foundation

Deliverables:

- `lean-toolchain` pinned;
- `lakefile.lean` created;
- mathlib dependency selected;
- `LaxCert` namespace created;
- CI builds empty project;
- no-sorry gate added.

Exit criterion:

```bash
lake build
```

passes from a clean checkout.

## Phase 1 — Scalar expression and jet algebra

Deliverables:

- field names `u,p,q`;
- jet variables `(field, order)`;
- scalar expression AST;
- `Dx` shift on jets;
- polynomial simplification path;
- generated scalar equalities discharged by `ring_nf` or equivalent.

Exit criterion:

Certify simple identities such as:

\[
D_x(pq) = p_xq + pq_x.
\]

## Phase 2 — Differential operator normal form

Deliverables:

- bounded differential operators;
- Leibniz composition formula;
- coefficient extraction;
- commutator;
- residual zero criterion.

Exit criterion:

Certify:

\[
D_x \circ f = fD_x + f_x.
\]

and reject a wrong-sign version.

## Phase 3 — Matrix operator Lax equation

Deliverables:

- matrix differential operators;
- entrywise matrix composition;
- commutator;
- `SatisfiesLaxEquation`;
- generated candidate proof format.

Exit criterion:

Certify a nontrivial 2×2 LAXFORGE calibration candidate.

## Phase 4 — Formal adjoints

Deliverables:

- scalar formal adjoint;
- matrix formal adjoint;
- self-adjoint and skew-adjoint predicates;
- generated adjointness claims.

Exit criterion:

Certify declared `SelfAdjoint L` and `SkewAdjoint P` for the calibration candidate.

## Phase 5 — AETHER ledger integration

Deliverables:

- proof-status JSON;
- provenance record;
- hash discipline;
- failure taxonomy;
- append-only event interface.

Exit criterion:

Every CI proof creates a ledger-compatible proof-status object.

## Phase 6 — Gauge equivalence

Deliverables:

- gauge transform definitions;
- zero-curvature invariance theorem;
- generated gauge-equivalence certificates.

Exit criterion:

Certify that two candidates are gauge-equivalent under a declared gauge transform.

## Phase 7 — Prior-art and novelty discipline

Deliverables:

- invariant registry hooks;
- gauge-class IDs;
- prior-art match records;
- proof-supported novelty flags.

Exit criterion:

LAXFORGE can label candidates as:

- false;
- certified but known;
- certified and gauge-equivalent to known;
- certified and not matched by current invariants.
