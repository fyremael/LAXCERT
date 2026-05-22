from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from laxforge_laxcert.emitter_contract import (
    build_candidate,
    certify_candidate_input,
    emit_lean,
    sha256_text,
    validate_candidate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def assert_indexed_certificate_shape(source: str) -> None:
    assert "CoefficientAt" in source
    assert "CoefficientCertificate_indexed" in source
    assert "residual_coeff_" not in source
    assert "self_adjoint_L_coeff_" not in source
    assert "skew_adjoint_P_coeff_" not in source
    assert "And.intro" not in source
    assert " ∧ " not in source


def test_committed_generated_sources_match_deterministic_emission(tmp_path: Path) -> None:
    for candidate_name in [
        "toy_lax_zero.json",
        "matrix_2x2_zero.json",
        "matrix_2x2_offdiag_zero.json",
        "matrix_3x3_order2_zero.json",
    ]:
        candidate = json.loads((REPO_ROOT / "candidates" / candidate_name).read_text(encoding="utf-8"))
        generated_path = emit_lean(candidate, tmp_path)
        generated_text = generated_path.read_text(encoding="utf-8")
        committed_lean = REPO_ROOT / "lean" / "LaxCert" / "Generated" / generated_path.name
        artifact_dir = REPO_ROOT / "artifacts" / candidate["candidate_id"]

        assert committed_lean.read_text(encoding="utf-8") == generated_text
        assert (artifact_dir / "generated.lean").read_text(encoding="utf-8") == generated_text
        assert (artifact_dir / "generated.hash").read_text(encoding="utf-8").strip() == sha256_text(generated_text)


def test_valid_toy_candidate_succeeds() -> None:
    result = build_candidate(REPO_ROOT / "candidates" / "toy_lax_zero.json", REPO_ROOT)
    assert result.status == "proof_succeeded"
    assert result.generated_lean_hash is not None
    source = result.lean_file.read_text(encoding="utf-8")
    assert "theorem candidate_satisfies_lax_equation : True" not in source
    assert "laxCoefficientCertificate" in source
    assert_indexed_certificate_shape(source)


def test_matrix_2x2_candidate_succeeds() -> None:
    result = build_candidate(REPO_ROOT / "candidates" / "matrix_2x2_zero.json", REPO_ROOT)
    assert result.status == "proof_succeeded"
    source = result.lean_file.read_text(encoding="utf-8")
    assert "theorem candidate_satisfies_lax_equation : True" not in source
    assert "theorem candidate_self_adjoint_L : True" not in source
    assert "theorem candidate_skew_adjoint_P : True" not in source
    assert "selfAdjointLCoefficientCertificate" in source
    assert "skewAdjointPCoefficientCertificate" in source
    assert "def selfAdjointResidualL_0_0" in source
    assert "def skewAdjointResidualP_0_0" in source
    assert_indexed_certificate_shape(source)


def test_matrix_2x2_offdiag_candidate_succeeds() -> None:
    result = build_candidate(REPO_ROOT / "candidates" / "matrix_2x2_offdiag_zero.json", REPO_ROOT)
    assert result.status == "proof_succeeded"
    source = result.lean_file.read_text(encoding="utf-8")
    assert "theorem candidate_satisfies_lax_equation : True" not in source
    assert "theorem candidate_self_adjoint_L : True" not in source
    assert "theorem candidate_skew_adjoint_P : True" not in source
    assert "def L_0_1" in source
    assert "def L_1_0" in source
    assert "ScalarExpr.jetDx .p 0" in source
    assert "def laxResidual_0_1" in source
    assert "selfAdjointLCoefficientCertificate" in source
    assert "skewAdjointPCoefficientCertificate" in source
    assert_indexed_certificate_shape(source)


def test_matrix_3x3_order2_candidate_succeeds() -> None:
    result = build_candidate(REPO_ROOT / "candidates" / "matrix_3x3_order2_zero.json", REPO_ROOT)
    assert result.status == "proof_succeeded"
    source = result.lean_file.read_text(encoding="utf-8")
    assert "MatrixOp 3 ScalarExpr 2" in source
    assert "MatrixOp 3 ScalarExpr 3" in source
    assert "BoundedDiffOp.composeToBound 3" in source
    assert "BoundedDiffOp.formalAdjointBounded" in source
    assert "BoundedDiffOp.composeFirstOrder" not in source
    assert "BoundedDiffOp.formalAdjointFirstOrder" not in source
    assert "def L_0_0" in source
    assert "def laxResidual_0_0" in source
    assert_indexed_certificate_shape(source)
    assert len(source.splitlines()) < 300


def test_indexed_certificate_scales_to_4x4_order3(tmp_path: Path) -> None:
    def const_expr(value: int) -> dict[str, Any]:
        return {"kind": "const", "value": value}

    def op(order: int, value: int) -> dict[str, Any]:
        return {"terms": [{"order": order, "coeff": const_expr(value)}]}

    size = 4
    candidate_id = "TmpMatrix4x4Order3Zero"
    candidate = {
        "schema_version": "0.1.0",
        "laxcert_schema_version": "0.1.0",
        "candidate_id": candidate_id,
        "laxforge_version": "internal-fixture",
        "laxcert_target_version": "0.1.0",
        "scalar_ring": "rat_differential_polynomial",
        "directions": {"space": ["x"], "time": "t"},
        "fields": ["u"],
        "evolution": {"u": const_expr(0)},
        "operators": {
            "L": {
                "rows": [
                    [op(2, 1) if i == j else op(0, 0) for j in range(size)]
                    for i in range(size)
                ]
            },
            "P": {
                "rows": [
                    [op(3, 1) if i == j else op(0, 0) for j in range(size)]
                    for i in range(size)
                ]
            },
        },
        "claims": [
            {"type": "lax_equation", "proof_strategy": "coefficient_certificate"},
            {"type": "self_adjoint_L", "proof_strategy": "coefficient_certificate"},
            {"type": "skew_adjoint_P", "proof_strategy": "coefficient_certificate"},
        ],
        "assumptions": [
            "formal differential operators over commuting scalar coefficients",
            "formal adjoint ignores boundary terms",
        ],
        "provenance": {"source": "pytest_scale_fixture"},
    }
    candidate_path = tmp_path / "matrix_4x4_order3_zero.json"
    candidate_path.write_text(json.dumps(candidate, indent=2), encoding="utf-8")

    result = build_candidate(candidate_path, REPO_ROOT)
    try:
        assert result.status == "proof_succeeded"
        source = result.lean_file.read_text(encoding="utf-8")
        assert "MatrixOp 4 ScalarExpr 5" in source
        assert "BoundedDiffOp.composeToBound 5" in source
        assert "def laxResidual_3_3" in source
        assert_indexed_certificate_shape(source)
        assert len(source.splitlines()) < 450
    finally:
        if result.lean_file is not None:
            result.lean_file.unlink(missing_ok=True)
        shutil.rmtree(REPO_ROOT / "artifacts" / candidate_id, ignore_errors=True)


def test_laxforge_artifact_directory_ingests_external_candidate(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "laxforge_artifact"
    artifact_dir.mkdir()
    candidate = json.loads((REPO_ROOT / "candidates" / "toy_lax_zero.json").read_text(encoding="utf-8"))
    candidate["candidate_id"] = "ExternalLaxforgeToyZero"
    candidate["laxforge_version"] = "git:test-laxforge-export"
    candidate["provenance"] = {
        "source": "laxforge",
        "artifact_kind": "external_calibration_fixture",
    }
    candidate_path = artifact_dir / "candidate.json"
    candidate_path.write_text(json.dumps(candidate, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path = artifact_dir / "laxforge_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "artifact_type": "laxforge.candidate_export",
                "candidate_json": "candidate.json",
                "laxforge_version": "git:test-laxforge-export",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    result = certify_candidate_input(artifact_dir, REPO_ROOT)
    try:
        assert result.status == "proof_succeeded"
        artifact_out = REPO_ROOT / "artifacts" / "ExternalLaxforgeToyZero"
        source_doc = json.loads((artifact_out / "candidate-source.json").read_text(encoding="utf-8"))
        status_doc = json.loads((artifact_out / "proof-status.json").read_text(encoding="utf-8"))
        assert source_doc["source_kind"] == "laxforge_artifact_dir"
        assert source_doc["manifest_hash"].startswith("sha256:")
        assert status_doc["candidate_source"]["source_kind"] == "laxforge_artifact_dir"
        assert result.lean_file.read_text(encoding="utf-8").count("laxCoefficientCertificate_indexed") == 2
    finally:
        if result.lean_file is not None:
            result.lean_file.unlink(missing_ok=True)
        shutil.rmtree(REPO_ROOT / "artifacts" / "ExternalLaxforgeToyZero", ignore_errors=True)


def test_false_candidate_reports_nonzero_residual() -> None:
    result = build_candidate(REPO_ROOT / "candidates" / "false_wrong_sign.json", REPO_ROOT)
    assert result.status == "proof_failed_nonzero_residual"
    assert result.residual_witness is not None
    assert result.residual_witness["residual_display"] == "2*p_1^1"


def assert_aether_ledger_common(status_doc: dict[str, Any]) -> None:
    assert status_doc["candidate_hash"].startswith("sha256:")
    assert status_doc["laxforge_version"]
    assert status_doc["laxcert_version"].startswith("laxcert:")
    assert status_doc["lean_toolchain"].startswith("leanprover/lean4:")
    assert status_doc["mathlib_revision"].startswith("git:")
    assert status_doc["timestamp_utc"].endswith("Z")
    assert status_doc["build_log_uri"].endswith("lake-build.log")


def test_proof_status_records_aether_ledger_fields() -> None:
    success = build_candidate(REPO_ROOT / "candidates" / "matrix_2x2_offdiag_zero.json", REPO_ROOT)
    assert success.status == "proof_succeeded"
    success_status = json.loads(
        (REPO_ROOT / "artifacts" / "Matrix2x2OffDiagonalZero" / "proof-status.json").read_text(encoding="utf-8")
    )
    assert_aether_ledger_common(success_status)
    assert success_status["event_type"] == "laxcert.proof.succeeded"
    assert success_status["generated_lean_hash"].startswith("sha256:")
    assert success_status["assumptions_hash"].startswith("sha256:")

    failure = build_candidate(REPO_ROOT / "candidates" / "false_wrong_sign.json", REPO_ROOT)
    assert failure.status == "proof_failed_nonzero_residual"
    failure_status = json.loads(
        (REPO_ROOT / "artifacts" / "FalseWrongSign" / "proof-status.json").read_text(encoding="utf-8")
    )
    assert_aether_ledger_common(failure_status)
    assert failure_status["event_type"] == "laxcert.proof.failed"
    assert failure_status["residual_witness"]["residual_display"] == "2*p_1^1"


def test_schema_rejects_malformed_scalar_ast() -> None:
    candidate = json.loads((REPO_ROOT / "candidates" / "toy_lax_zero.json").read_text(encoding="utf-8"))
    candidate["evolution"]["p"] = {"kind": "jet", "field": "p"}
    errors = validate_candidate(candidate, REPO_ROOT)
    assert errors


def test_schema_accepts_spec_required_metadata() -> None:
    candidate = json.loads((REPO_ROOT / "candidates" / "toy_lax_zero.json").read_text(encoding="utf-8"))
    errors = validate_candidate(candidate, REPO_ROOT)
    assert errors == []
    assert candidate["laxcert_schema_version"] == candidate["schema_version"]
    assert candidate["laxforge_version"]
    assert candidate["provenance"]["source"]


def test_schema_rejects_undeclared_jet_field() -> None:
    candidate = json.loads((REPO_ROOT / "candidates" / "toy_lax_zero.json").read_text(encoding="utf-8"))
    candidate["operators"]["L"]["rows"][0][0]["terms"][0]["coeff"] = {
        "kind": "jet",
        "field": "q",
        "order": 0,
    }
    errors = validate_candidate(candidate, REPO_ROOT)
    assert any("jet field 'q' is not declared" in error for error in errors)


def test_schema_rejects_duplicate_operator_orders() -> None:
    candidate = json.loads((REPO_ROOT / "candidates" / "toy_lax_zero.json").read_text(encoding="utf-8"))
    candidate["operators"]["P"]["rows"][0][0]["terms"].append(
        {"order": 1, "coeff": {"kind": "const", "value": 2}}
    )
    errors = validate_candidate(candidate, REPO_ROOT)
    assert any("duplicate differential order 1" in error for error in errors)


def test_schema_rejects_non_square_operator_matrix() -> None:
    candidate = json.loads((REPO_ROOT / "candidates" / "toy_lax_zero.json").read_text(encoding="utf-8"))
    candidate["operators"]["L"]["rows"] = [
        [
            {"terms": [{"order": 0, "coeff": {"kind": "const", "value": 1}}]},
            {"terms": [{"order": 0, "coeff": {"kind": "const", "value": 0}}]},
        ]
    ]
    errors = validate_candidate(candidate, REPO_ROOT)
    assert any("matrix must be square" in error for error in errors)


def test_deterministic_emission_hash() -> None:
    first = build_candidate(REPO_ROOT / "candidates" / "toy_lax_zero.json", REPO_ROOT)
    second = build_candidate(REPO_ROOT / "candidates" / "toy_lax_zero.json", REPO_ROOT)
    assert first.generated_lean_hash == second.generated_lean_hash
