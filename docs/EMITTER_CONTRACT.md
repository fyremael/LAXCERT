# Python-to-Lean Emitter Contract

## 1. Role

The emitter is the bridge from LAXFORGE to LAXCERT. It converts a structured candidate certificate into Lean source files and invokes Lean's build system.

The emitter is not trusted as a proof. It is trusted only to produce files that Lean can check.

## 2. Inputs

Required logical input:

```text
candidate.json
```

Accepted physical inputs:

```text
candidate.json
laxforge_artifact_dir/
  laxforge_manifest.json
  candidate.json
laxforge_manifest.json
```

For LAXFORGE artifact directories or standalone manifests, `laxforge_manifest.json`
must declare one of:

```json
{
  "candidate_json": "candidate.json"
}
```

The aliases `candidate_path` and `laxcert_candidate_json` are also accepted.
Paths are resolved relative to the manifest directory.

Optional inputs:

```text
candidate.normalized.json
prior_art.json
gauge_metadata.json
```

## 3. Output files

```text
lean/LaxCert/Generated/<CandidateName>.lean
artifacts/<candidate_id>/proof-status.json
artifacts/<candidate_id>/lake-build.log
artifacts/<candidate_id>/generated.hash
```

## 4. AST discipline

Never use unparsed strings as the authoritative expression format.

Bad:

```json
{"expr": "p*q + D(x,x)(u)"}
```

Good:

```json
{
  "kind": "add",
  "args": [
    {"kind": "mul", "args": [{"kind": "jet", "field": "p", "order": 0}, {"kind": "jet", "field": "q", "order": 0}]},
    {"kind": "jet", "field": "u", "order": 2}
  ]
}
```

Strings may be included for display only:

```json
{"display": "p*q + u_xx"}
```

## 5. Normalization pipeline

The emitter runs:

```text
validate_schema(candidate)
  → collect_fields(candidate)
  → infer_max_orders(candidate)
  → normalize_scalar_exprs(candidate)
  → expand_operator_compositions(candidate)
  → coefficient_match_residual(candidate)
  → emit_lean_defs(candidate)
  → emit_lean_theorems(candidate)
  → lake_build(candidate)
  → proof_status(candidate)
```

## 6. Generated theorem shape

Generated Lean should be boring and explicit.

Preferred theorem shape:

```lean
namespace LaxCert.Generated.Candidate001

open LaxCert

def L : MatrixOp 2 ScalarRing maxOrder := ...
def P : MatrixOp 2 ScalarRing maxOrder := ...
def Dt : ScalarRing → ScalarRing := ...

theorem residual_coeff_00_0 : ... := by ring_nf
theorem residual_coeff_00_1 : ... := by ring_nf
-- many generated coefficient facts

theorem candidate_satisfies_lax_equation :
  SatisfiesLaxEquation Dt L P := by
  apply residual_zero_of_all_coeff_zero
  exact residual_coeff_00_0
  exact residual_coeff_00_1
  ...

end LaxCert.Generated.Candidate001
```

## 7. Proof strategy escalation

The emitter should try proof modes in order:

1. direct `rfl` after normalization;
2. `simp` with LAXCERT normal-form lemmas;
3. `ring_nf` for scalar polynomial equalities;
4. generated coefficient lemmas;
5. fail with residual witness.

No candidate should pass by assuming the target theorem.

## 8. Residual witness

On failure, produce a witness such as:

```json
{
  "status": "failed_nonzero_residual",
  "entry": [0,1],
  "operator_order": 0,
  "residual_display": "2*p*q_x - p_x*q",
  "normalized_ast": {...}
}
```

This lets LAXFORGE learn from failure.

## 9. Determinism

Generated Lean must be stable:

```text
same candidate JSON + same emitter version = same emitted Lean hash
```

Sort keys. Canonicalize names. Avoid timestamped definitions inside Lean files.
