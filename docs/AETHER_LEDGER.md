# AETHER Ledger Contract for LAXCERT

## 1. Purpose

AETHER records the proof state of mathematical artifacts. It should not perform the proof. It should record what was claimed, what was checked, under which assumptions, using which toolchain, and with which result.

## 2. Ledger event types

### `laxforge.candidate.created`

Emitted when LAXFORGE creates a candidate.

### `laxcert.candidate.validated`

Emitted after schema validation.

### `laxcert.lean.emitted`

Emitted after deterministic Lean file generation.

### `laxcert.proof.succeeded`

Emitted after `lake build` passes for the candidate theorem.

### `laxcert.proof.failed`

Emitted when validation, emission, elaboration, or proof fails.

### `laxcert.gauge_equiv.succeeded`

Post-MVP event indicating certified gauge equivalence.

## 3. Minimal proof-status record

```json
{
  "event_type": "laxcert.proof.succeeded",
  "candidate_id": "candidate_001",
  "claim_type": "lax_equation",
  "lean_theorem": "LaxCert.Generated.Candidate001.candidate_satisfies_lax_equation",
  "candidate_hash": "sha256:...",
  "generated_lean_hash": "sha256:...",
  "laxforge_version": "git:...",
  "laxcert_version": "git:...",
  "lean_toolchain": "leanprover/lean4:<pinned>",
  "mathlib_revision": "git:...",
  "assumptions_hash": "sha256:...",
  "timestamp_utc": "...",
  "build_log_uri": "..."
}
```

## 4. Assumptions are first-class

A candidate may be certified under assumptions. Those assumptions must be visible.

Examples:

- field variables commute;
- `Dx` and `Dt` commute on generated jets;
- boundary terms ignored for formal adjoint;
- coefficient ring is characteristic zero;
- gauge matrix is invertible.

A proof without visible assumptions is not acceptable for Grand Challenge Labs artifact governance.
