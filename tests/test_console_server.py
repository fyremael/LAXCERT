from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from laxforge_laxcert.console_server import ConsoleBackend


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_console_summary_lists_candidates_artifacts_and_commands() -> None:
    backend = ConsoleBackend(REPO_ROOT, start_worker=False)
    try:
        summary = backend.summary()
    finally:
        backend.close()

    command_names = {command["name"] for command in summary["commands"]}
    candidate_ids = {candidate["candidate_id"] for candidate in summary["candidates"]}
    artifact_ids = {artifact["candidate_id"] for artifact in summary["artifacts"]}

    assert {"validate_candidate", "certify_candidate", "lake_build", "pytest"} <= command_names
    assert "ToyLaxZero" in candidate_ids
    assert "AKNSD2TransportZero" in candidate_ids
    assert "FalseWrongSign" in artifact_ids
    assert summary["status_counts"]["proof_succeeded"] >= 1
    assert summary["lean_toolchain"].startswith("leanprover/lean4:")


def test_console_validation_job_runs_through_queue() -> None:
    backend = ConsoleBackend(REPO_ROOT)
    try:
        queued = backend.submit_job("validate_candidate", "candidates/toy_lax_zero.json")
        finished = backend.wait_for_job(queued["id"], timeout_seconds=10)
    finally:
        backend.close()

    assert finished["status"] == "succeeded"
    assert finished["result"]["candidate_id"] == "ToyLaxZero"
    assert finished["result"]["status"] == "schema_valid"


def test_console_expected_failure_command_passes_for_false_candidate(tmp_path: Path) -> None:
    candidate = json.loads((REPO_ROOT / "candidates" / "false_wrong_sign.json").read_text(encoding="utf-8"))
    candidate["candidate_id"] = "ConsoleFalseWrongSign"
    candidate_path = tmp_path / "console_false_wrong_sign.json"
    candidate_path.write_text(json.dumps(candidate, indent=2), encoding="utf-8")

    backend = ConsoleBackend(REPO_ROOT)
    try:
        queued = backend.submit_job("certify_expected_failure", str(candidate_path))
        finished = backend.wait_for_job(queued["id"], timeout_seconds=10)
    finally:
        backend.close()
        shutil.rmtree(REPO_ROOT / "artifacts" / "ConsoleFalseWrongSign", ignore_errors=True)

    assert finished["status"] == "succeeded"
    assert finished["result"]["candidate_id"] == "ConsoleFalseWrongSign"
    assert finished["result"]["status"] == "proof_failed_nonzero_residual"


def test_console_file_reads_are_repo_scoped() -> None:
    backend = ConsoleBackend(REPO_ROOT, start_worker=False)
    try:
        proof_status = backend.read_repo_file("artifacts/ToyLaxZero/proof-status.json")
        assert "proof_succeeded" in proof_status["text"]

        with pytest.raises(ValueError):
            backend.read_repo_file("../outside.json")
    finally:
        backend.close()
