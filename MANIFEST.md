# Manifest

- `README.md`: overview and usage intent.
- `SPEC.md`: main specification.
- `docs/ARCHITECTURE.md`: system architecture.
- `docs/LEAN_API.md`: Lean theorem/API contract.
- `docs/PROOF_OBLIGATIONS.md`: proof obligations and acceptance tests.
- `docs/EMITTER_CONTRACT.md`: Python-to-Lean emitter contract.
- `docs/AETHER_LEDGER.md`: AETHER proof ledger contract.
- `docs/ROADMAP.md`: phased execution plan.
- `schemas/laxcert_candidate.schema.json`: candidate certificate schema.
- `python/laxforge_laxcert/emitter_contract.py`: Python skeleton.
- `candidates/`: internal positive and false MVP fixture certificates.
- `artifacts/`: generated proof-status, hashes, logs, normalized JSON, and Lean outputs.
- `tests/`: pytest coverage for schema validation, deterministic emission, positive proofs, and false-candidate failure.
- `.github/workflows/laxcert-ci.yml`: executable MVP CI workflow.
- `lean/`: Lean project with phase 1 scalar jet algebra, toy scalar proof, and initial phase 2 operator-normal-form proof.
- `ci/GITHUB_ACTIONS.md`: CI plan.
