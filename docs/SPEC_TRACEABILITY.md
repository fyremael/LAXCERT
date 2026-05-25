# SPEC Traceability and Gap Register

Last updated: 2026-05-22

This document tracks `SPEC.md` section 13 in order. Do not advance remediation to a later item until the current item is complete or explicitly deferred.

## Section 13 MVP Definition Of Done

| Item | Requirement | Status | Evidence | Gap | Next remediation |
| --- | --- | --- | --- | --- | --- |
| 1 | A candidate JSON can be emitted from LAXFORGE. | Complete for MVP. | Merged LAXFORGE PR `fyremael/LAXFORGE#4` adds `scripts/export_laxcert_calibration.py`; merge commit `a27c258598e5beaed785ca3a1bbb94056dc7de0b`; artifact exported from LAXFORGE `main` at `runs/laxcert_calibration_merged` certified through `certify_candidate_input` with `status: proof_succeeded`; `proof-status.json` records `source_kind: laxforge_artifact_dir` and manifest hash. | None for MVP. | Preserve optional external artifact CI gate. |
| 2 | The JSON validates against the schema. | Remediated for MVP schema contract. | `laxcert_candidate.schema.json` now requires spec metadata including `laxcert_schema_version`, `laxforge_version`, assumptions, and provenance source; `validate_candidate` rejects undeclared jets, duplicate differential orders, non-square/non-rectangular matrices, shape mismatches, and evolution-field drift; pytest covers valid metadata plus malformed AST, undeclared field, duplicate order, and non-square matrix failures. | Zero-curvature, gauge, prior-art, and gauge-reduction metadata are schema-admitted but remain post-MVP proof obligations. | Proceed to item 3 deterministic regeneration CI comparison. |
| 3 | Lean files are generated deterministically. | Remediated for MVP CI. | `test_committed_generated_sources_match_deterministic_emission` compares fresh emitter output with committed generated Lean and artifact hashes; `.github/workflows/laxcert-ci.yml` runs `git diff --exit-code` over committed generated Lean/hash files after positive candidate regeneration. | None for current positive fixtures; external LAXFORGE artifact remains optional and is not committed. | Preserve deterministic regeneration gate. |
| 4 | Hand-written Lean modules compile. | Complete for MVP. | `lake -R build LaxCert` passed on 2026-05-22; production/generated no-sorry/admit/axiom scan returned no matches. | None known. | Preserve in CI and reconfirm during item 9 clean-checkout pass. |
| 5 | At least one toy Lax equation compiles. | Complete for MVP. | `ToyLaxZero` certifies with `status: proof_succeeded`; generated theorem is a coefficient certificate, not `True := by trivial`; pytest regression covers generated theorem shape. | None known. | Preserve regression. |
| 6 | At least one nontrivial 2x2 differential-operator candidate compiles. | Complete for MVP; section-10 transport calibration added. | `Matrix2x2OffDiagonalZero` certifies with `status: proof_succeeded`; `AKNSD2TransportZero` certifies the `SPEC.md` section-10 `L = [[D_x^2, -q], [p, -D_x^2]]` shape with `P = D_x I`, `p_t = p_x`, `q_t = q_x`; committed `LaxforgeAKNSD2TransportZero` producer artifact certifies and is included in CI deterministic checks. | Full nonlinear AKNS/mKdV hierarchy calibration remains post-transport milestone. | Preserve off-diagonal, section-10 transport, and LAXFORGE producer regressions; next target is nonlinear section-10 `P`. |
| 7 | At least one intentionally false candidate fails. | Complete for MVP. | `FalseWrongSign` reports `proof_failed_nonzero_residual` with witness `entry: [0,0]`, `operator_order: 0`, `residual_display: 2*p_1^1`; CLI `--expect-failure` exits successfully and CI runs the gate. | Add false adjoint and higher-order negative cases later. | Preserve non-negotiable false-candidate gate. |
| 8 | Proof status is recorded in an AETHER-compatible ledger object. | Complete for MVP. | `proof-status.json` now records candidate/generated/assumptions hashes, claim type, theorem, LAXFORGE version, LAXCERT version, Lean toolchain, mathlib revision, timestamp, build log URI, schema versions, and source metadata for external artifacts; pytest covers success and residual-failure ledger fields. | Append-only event streaming remains post-MVP. | Proceed to item 9 clean-checkout CI validation. |
| 9 | The entire process runs in CI from a clean checkout. | Complete for MVP. | GitHub Actions clean-checkout run `https://github.com/fyremael/LAXCERT/actions/runs/26316729927` passed on 2026-05-22; workflow ran Lean build, no-admission scan, Python install, positive toy/2x2/off-diagonal/3x3 generation, deterministic `git diff`, optional LAXFORGE artifact gate, false-candidate expected failure, and pytest. | None for MVP. | Preserve workflow as the required release gate. |

## Item 1 Closeout Notes

Requirement: prove LAXCERT can consume a candidate JSON emitted from LAXFORGE, not only repository-internal fixtures.

Implemented behavior:

- Direct candidate JSON input remains supported.
- A LAXFORGE artifact directory is supported when it contains either:
  - `laxforge_manifest.json` with `candidate_json`, `candidate_path`, or `laxcert_candidate_json`; or
  - a candidate file named `candidate.json`, `laxcert_candidate.json`, or `laxforge_candidate.json`.
- A standalone manifest JSON file is supported with the same candidate path fields.
- The certifier writes `artifacts/<candidate_id>/candidate-source.json` for LAXFORGE artifact inputs.
- `proof-status.json` includes `candidate_source` metadata for artifact-ingested candidates.
- CI supports an optional `LAXFORGE_ARTIFACT_PATH` environment variable. When set to an existing path, it certifies that artifact using the same CLI entrypoint.

Verification:

```bash
pytest tests/test_emitter_pipeline.py::test_laxforge_artifact_directory_ingests_external_candidate
```

Acceptance for MVP item 1:

- The ingestion API proves LAXCERT is not restricted to `candidates/*.json`.
- The pytest fixture simulates the exact external boundary: a LAXFORGE export directory with a manifest and candidate JSON.
- Merged LAXFORGE PR `https://github.com/fyremael/LAXFORGE/pull/4` supplies the real producer-side calibration exporter. The artifact generated from merged LAXFORGE `main` certified successfully through the same external input path.

## Item 2 Closeout Notes

Requirement: prove candidate JSON is not merely accepted by the Python emitter, but validated against the declared MVP certificate schema from `SPEC.md` section 5.

Implemented behavior:

- The schema requires the spec-named `laxcert_schema_version` field while retaining `schema_version` compatibility.
- The schema requires `laxforge_version`, `scalar_ring`, `directions`, `fields`, `evolution`, `operators`, `claims`, `assumptions`, and `provenance.source`.
- The schema admits future `prior_art` and `gauge_reduction` metadata without making those post-MVP claims mandatory.
- The semantic validator checks field/evolution equality, rejects jet variables outside the declared field set, rejects duplicate differential-operator orders, enforces square operator matrices for generated certificates, and checks L/P and U/V shape agreement.
- Merged LAXFORGE PR `fyremael/LAXFORGE#4` emits `laxcert_schema_version`; the merged-main generated artifact still certifies with `status: proof_succeeded`.

Verification:

```bash
pytest -q
python -m laxforge_laxcert.emitter_contract F:\_codex\LAXFORGE\runs\laxcert_calibration_merged --repo-root .
```

Acceptance for MVP item 2:

- Valid internal and external candidate JSON passes schema and semantic validation.
- Malformed scalar AST, undeclared fields, duplicate operator orders, and non-square matrix candidates fail before Lean emission.

## Item 3 Closeout Notes

Requirement: prove Lean generation is deterministic enough that a clean checkout can detect stale or drifted generated artifacts.

Implemented behavior:

- Pytest emits fresh Lean into a temporary directory for `ToyLaxZero`, `Matrix2x2Zero`, `Matrix2x2OffDiagonalZero`, and `Matrix3x3Order2Zero`.
- The test compares that fresh source against both `lean/LaxCert/Generated/<Candidate>.lean` and `artifacts/<Candidate>/generated.lean`.
- The test recomputes the source hash and compares it against `artifacts/<Candidate>/generated.hash`.
- CI regenerates the same positive candidates, then runs `git diff --exit-code` over the committed generated Lean and hash files.

Verification:

```bash
pytest -q
```

Acceptance for MVP item 3:

- Stale committed generated Lean or stale committed generated hashes now fail local pytest and CI.

## Item 6 Closeout Notes

Requirement: certify at least one 2x2 differential-operator candidate that is not only a diagonal smoke test.

Implemented behavior:

- Added `candidates/matrix_2x2_offdiag_zero.json`.
- The candidate uses
  - `L = [[0, p], [p, 0]]`;
  - `P = [[D_x, 0], [0, D_x]]`;
  - `p_t = p_x`.
- The Lax residual reduces to the first-order operator identity `D_x ∘ p - p ∘ D_x = p_x` in off-diagonal matrix entries.
- The candidate also certifies generated `SelfAdjoint L` and `SkewAdjoint P` coefficient certificates.
- CI now regenerates and diff-checks `Matrix2x2OffDiagonalZero` alongside the other positive fixtures.

Verification:

```bash
python -m laxforge_laxcert.emitter_contract candidates/matrix_2x2_offdiag_zero.json --repo-root .
pytest -q
cd lean && lake -R build LaxCert
```

Acceptance for MVP item 6:

- The committed positive 2x2 evidence now includes a genuine off-diagonal matrix differential-operator commutator proof.

## Section 10 Transport Calibration Notes

Requirement: move beyond the MVP smoke fixture toward the `SPEC.md` section-10 paired-field operator shape.

Implemented behavior:

- Added `candidates/akns_d2_transport_zero.json`.
- Added committed producer artifact `artifacts/LaxforgeAKNSD2TransportZero/` generated by LAXFORGE.
- Both candidates use
  - `L = [[D_x^2, -q], [p, -D_x^2]]`;
  - `P = [[D_x, 0], [0, D_x]]`;
  - `p_t = p_x`, `q_t = q_x`.
- The proof checks cancellation through residual order 3, including the diagonal `D_x^3` commutator terms.
- The candidate certifies `SkewAdjoint P`. It does not assert `SelfAdjoint L` because the MVP schema does not yet support the reduction assumption `p = -q`.
- CI regenerates and diff-checks both the internal section-10 transport fixture and the LAXFORGE-emitted section-10 artifact.

Verification:

```bash
python -m laxforge_laxcert.emitter_contract candidates/akns_d2_transport_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract artifacts/LaxforgeAKNSD2TransportZero/candidate.json --repo-root .
pytest -q
cd lean && lake -R build LaxCert
```

Acceptance for the section-10 transport milestone:

- The section-10 `D_x^2`/`p,q` operator shape is now checked by Lean from both an internal fixture and a LAXFORGE-emitted artifact.

## Item 8 Closeout Notes

Requirement: emit an AETHER-compatible proof-status object, not only a local build result.

Implemented behavior:

- All proof-status paths use shared ledger metadata:
  - `laxforge_version`;
  - `laxcert_version`;
  - `lean_toolchain`;
  - `mathlib_revision`;
  - `timestamp_utc`;
  - `build_log_uri`;
  - schema versions and candidate hash.
- Success records include generated Lean hash, normalized hash, assumptions hash, theorem name, claim type, and build log URI.
- Nonzero-residual failures include normalized hash, assumptions hash, claim type, residual witness, and build log URI even when Lean is not invoked.
- Schema and emission failures also write a log file and ledger-shaped failure record.
- External LAXFORGE artifact records preserve `candidate_source` metadata with manifest path and manifest hash.

Verification:

```bash
pytest -q
python -m laxforge_laxcert.emitter_contract F:\_codex\LAXFORGE\runs\laxcert_calibration_merged --repo-root .
```

Acceptance for MVP item 8:

- Internal success, internal false-candidate failure, and external LAXFORGE success all produce ledger-shaped `proof-status.json` records with the required MVP governance fields.

## Item 9 Closeout Notes

Requirement: prove the full process runs in CI from a clean checkout.

Implemented behavior:

- The workflow installs Lean through elan.
- It builds the hand-written Lean core.
- It scans production/generated modules for `sorry`, `admit`, and `axiom`.
- It installs the Python package with test dependencies.
- It certifies the positive toy, diagonal 2x2, off-diagonal 2x2, and 3x3 order-2 candidates.
- It runs deterministic regeneration comparison with `git diff --exit-code` over committed generated Lean and hash artifacts.
- It optionally certifies a supplied external `LAXFORGE_ARTIFACT_PATH`.
- It asserts the false candidate fails.
- It runs pytest.

Local verification before remote run:

```powershell
python -m pip install -e .[test]
lake -R build LaxCert --dir lean
rg -n "\b(sorry|admit|axiom)\b" lean\LaxCert python schemas tests candidates --glob '!**\__pycache__\**' --glob '!*.pyc'
python -m laxforge_laxcert.emitter_contract candidates/toy_lax_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/matrix_2x2_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/matrix_2x2_offdiag_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/matrix_3x3_order2_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/false_wrong_sign.json --repo-root . --expect-failure
pytest -q
```

Remote clean-checkout verification:

- Repository: `https://github.com/fyremael/LAXCERT`
- Workflow run: `https://github.com/fyremael/LAXCERT/actions/runs/26316729927`
- Result: passed, job `mvp` completed in 3m18s.

Acceptance for MVP item 9:

- The full MVP pipeline now runs from a GitHub clean checkout and records a passing Actions run URL.
