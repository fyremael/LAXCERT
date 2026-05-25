# LAXCERT: Lean4 Companion Specification for LAXFORGE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/fyremael/LAXCERT/actions/workflows/laxcert-ci.yml/badge.svg)](https://github.com/fyremael/LAXCERT/actions/workflows/laxcert-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Lean 4.29.1](https://img.shields.io/badge/Lean-4.29.1-brightgreen.svg)](lean/lean-toolchain)

**Status:** MVP proof pipeline implemented for internal fixtures, with generated Lean/artifact emission and CI gates.
**Owner context:** Grand Challenge Labs / LAXFORGE.
**Purpose:** make LAXFORGE a gauge-aware, proof-producing discovery engine for Lax pairs, zero-curvature representations, and operator identities.

Core doctrine:

> LAXFORGE proposes. LAXCERT certifies. AETHER records. MODULUS interprets.

LAXFORGE remains the search and symbolic-discovery engine. LAXCERT is the Lean4 companion that receives structured certificates and machine-checks their algebraic claims.

This pack contains:

- `SPEC.md` — main product and research specification.
- `docs/ARCHITECTURE.md` — component diagram and data flow.
- `docs/LEAN_API.md` — Lean module contracts and theorem surface.
- `docs/PROOF_OBLIGATIONS.md` — exact proof goals and acceptance tests.
- `docs/EMITTER_CONTRACT.md` — Python/SymPy-to-Lean certificate interface.
- `docs/AETHER_LEDGER.md` — proof provenance and governance records.
- `docs/ROADMAP.md` — build phases and milestones.
- `docs/SPEC_TRACEABILITY.md` — ordered section 13 gap register and closeout evidence.
- `docs/CONSOLE.md` — local visual console for candidates, artifacts, job queue, and operator commands.
- `schemas/laxcert_candidate.schema.json` — JSON schema for emitted candidate certificates.
- `python/laxforge_laxcert/emitter_contract.py` — typed Python-side contract sketch.
- `lean/` — Lean project skeleton and illustrative module boundaries.
- `ci/GITHUB_ACTIONS.md` — CI gates and failure modes.

Phase 1 implementation status:

- field names `u`, `p`, and `q`;
- jet variables as `(field, order)`;
- scalar expression AST with rational constants, jets, sums, products, negation, and powers;
- spatial derivation `Dx`, including jet shifting and product rule;
- lightweight scalar simplification for generated proof targets;
- toy theorem certifying `D_x(pq) = p_x q + p q_x`.

Initial phase 2 implementation status:

- bounded differential operator coefficient structure with zero/add/neg/sub instances;
- coefficient extensionality theorem;
- first-order operator constructors for multiplication by a scalar and `D_x`;
- first-order Leibniz/Ore composition into second-order normal form;
- toy theorem certifying `D_x ∘ p = p_x + pD_x`;
- wrong-sign rejection theorem for the same toy identity.

MVP pipeline status:

- exact Lean toolchain pinned to `leanprover/lean4:v4.29.1`;
- mathlib dependency declared at tag `v4.29.1`;
- Python package baseline via `pyproject.toml`;
- strict candidate schema validation;
- deterministic Python normalization and Lean emission;
- generated artifact folders under `artifacts/<candidate_id>/`;
- internal positive toy candidate, internal diagonal and off-diagonal 2x2 candidates, and false-candidate failure gate;
- section-10 transport calibration for `L = [[D_x^2, -q], [p, -D_x^2]]`, including a committed LAXFORGE-emitted artifact;
- generated Lean coefficient certificates for toy and 2x2 fixtures, replacing vacuous `True` theorems;
- GitHub Actions workflow for Lean, schema/emitter, generated positives, false negative, and pytest.

Local verification:

```bash
cd lean
lake -R build LaxCert
cd ..
pytest
python -m laxforge_laxcert.emitter_contract candidates/toy_lax_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/matrix_2x2_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/matrix_2x2_offdiag_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/akns_d2_transport_zero.json --repo-root .
python -m laxforge_laxcert.emitter_contract artifacts/LaxforgeAKNSD2TransportZero/candidate.json --repo-root .
python -m laxforge_laxcert.emitter_contract candidates/false_wrong_sign.json --repo-root . --expect-failure
```

Local visual console:

```bash
python -m laxforge_laxcert.console_server --repo-root .
```

Open `http://127.0.0.1:8765` to inspect candidates, proof artifacts, the command queue, Lake/Pytest runs, and certifier results.

For Lean/mathlib dependency refreshes, prefer WSL native storage rather than
building from `/mnt/<drive>`. A reliable workflow is:

```bash
rsync -a --exclude=.lake --exclude=artifacts --exclude=.pytest_cache /mnt/f/_codex/LAXCERT/ ~/LAXCERT-wsl/
cd ~/LAXCERT-wsl/lean
lake update
lake -R build LaxCert
```

The MVP targets the current LAXFORGE scope: one spatial direction `x`; scalar fields `u` or paired fields `p,q`; formal differential operators written as powers of `D(x)`; self-adjoint `L`; skew-adjoint `P`; and certification of identities such as

\[
L_t = [P,L]
\]

or, for matrix connections,

\[
U_t - V_x + [U,V] = 0.
\]
