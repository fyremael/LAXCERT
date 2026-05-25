"""Local visual console backend for LAXCERT candidates, artifacts, and proof jobs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from queue import Queue
from threading import Lock, Thread
from typing import Any
from urllib.parse import parse_qs, urlparse
import argparse
import json
import mimetypes
import os
import subprocess
import uuid

from laxforge_laxcert.emitter_contract import (
    certify_candidate_input,
    lean_toolchain,
    load_candidate,
    mathlib_revision,
    matrix_bound,
    resolve_candidate_input,
    run_lake_build,
    utc_timestamp,
    validate_candidate,
)


COMMANDS: dict[str, dict[str, Any]] = {
    "validate_candidate": {
        "label": "Validate Schema",
        "description": "Resolve a candidate input and run schema plus semantic validation.",
        "requires_path": True,
        "default_path": "candidates/toy_lax_zero.json",
    },
    "certify_candidate": {
        "label": "Certify Candidate",
        "description": "Normalize, emit Lean, run Lake, and write proof-status artifacts.",
        "requires_path": True,
        "default_path": "candidates/toy_lax_zero.json",
    },
    "certify_expected_failure": {
        "label": "Certify Expected Failure",
        "description": "Run the certifier and pass only when the candidate does not prove.",
        "requires_path": True,
        "default_path": "candidates/false_wrong_sign.json",
    },
    "lake_build": {
        "label": "Lake Build",
        "description": "Build the Lean core with lake -R build LaxCert.",
        "requires_path": False,
    },
    "pytest": {
        "label": "Pytest",
        "description": "Run the Python regression suite.",
        "requires_path": False,
    },
}


@dataclass
class ConsoleJob:
    id: str
    command: str
    label: str
    input_path: str | None
    status: str = "queued"
    queued_at: str = field(default_factory=utc_timestamp)
    started_at: str | None = None
    finished_at: str | None = None
    exit_code: int | None = None
    log: list[str] = field(default_factory=list)
    result: dict[str, Any] | None = None


class ConsoleBackend:
    """Repository-aware service layer used by both the HTTP UI and tests."""

    def __init__(self, repo_root: Path, *, start_worker: bool = True) -> None:
        self.repo_root = repo_root.resolve()
        self._jobs: dict[str, ConsoleJob] = {}
        self._lock = Lock()
        self._queue: Queue[str | None] = Queue()
        self._worker: Thread | None = None
        if start_worker:
            self._worker = Thread(target=self._worker_loop, daemon=True)
            self._worker.start()

    def close(self) -> None:
        if self._worker is not None:
            self._queue.put(None)
            self._worker.join(timeout=2)
            self._worker = None

    def command_specs(self) -> list[dict[str, Any]]:
        return [{"name": name, **spec} for name, spec in COMMANDS.items()]

    def summary(self) -> dict[str, Any]:
        candidates = self.list_candidates()
        artifacts = self.list_artifacts()
        status_counts: dict[str, int] = {}
        for artifact in artifacts:
            status = str(artifact.get("status", "unknown"))
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "repo_root": str(self.repo_root),
            "lean_toolchain": self._safe_toolchain(),
            "mathlib_revision": self._safe_mathlib_revision(),
            "candidate_count": len(candidates),
            "artifact_count": len(artifacts),
            "status_counts": status_counts,
            "commands": self.command_specs(),
            "candidates": candidates,
            "artifacts": artifacts,
            "jobs": self.list_jobs(),
        }

    def list_candidates(self) -> list[dict[str, Any]]:
        paths: list[tuple[str, Path]] = []
        paths.extend(("candidate", path) for path in sorted((self.repo_root / "candidates").glob("*.json")))
        paths.extend(("artifact", path) for path in sorted((self.repo_root / "artifacts").glob("*/candidate.json")))

        candidates: list[dict[str, Any]] = []
        seen: set[Path] = set()
        for source_kind, path in paths:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidates.append(self._candidate_summary(path, source_kind))
        return sorted(candidates, key=lambda item: (str(item.get("candidate_id", "")), str(item.get("path", ""))))

    def list_artifacts(self) -> list[dict[str, Any]]:
        artifacts: list[dict[str, Any]] = []
        for status_path in sorted((self.repo_root / "artifacts").glob("*/proof-status.json")):
            try:
                status_doc = json.loads(status_path.read_text(encoding="utf-8"))
                artifact_dir = status_path.parent
                artifacts.append(
                    {
                        "candidate_id": status_doc.get("candidate_id", artifact_dir.name),
                        "status": status_doc.get("status", "unknown"),
                        "event_type": status_doc.get("event_type"),
                        "claim_type": status_doc.get("claim_type"),
                        "timestamp_utc": status_doc.get("timestamp_utc"),
                        "lean_theorem": status_doc.get("lean_theorem"),
                        "candidate_hash": status_doc.get("candidate_hash"),
                        "generated_lean_hash": status_doc.get("generated_lean_hash"),
                        "build_log_uri": status_doc.get("build_log_uri"),
                        "residual_witness": status_doc.get("residual_witness"),
                        "candidate_source": status_doc.get("candidate_source"),
                        "path": self._display_path(artifact_dir),
                    }
                )
            except Exception as exc:
                artifacts.append(
                    {
                        "candidate_id": status_path.parent.name,
                        "status": "unreadable",
                        "error": str(exc),
                        "path": self._display_path(status_path.parent),
                    }
                )
        return sorted(artifacts, key=lambda item: str(item.get("candidate_id", "")))

    def list_jobs(self) -> list[dict[str, Any]]:
        with self._lock:
            jobs = [asdict(job) for job in self._jobs.values()]
        return sorted(jobs, key=lambda job: str(job["queued_at"]), reverse=True)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return asdict(job) if job is not None else None

    def submit_job(self, command: str, input_path: str | None = None) -> dict[str, Any]:
        if command not in COMMANDS:
            raise ValueError(f"unsupported command: {command}")
        spec = COMMANDS[command]
        if spec["requires_path"] and not input_path:
            input_path = str(spec.get("default_path", ""))
        job = ConsoleJob(
            id=uuid.uuid4().hex[:12],
            command=command,
            label=str(spec["label"]),
            input_path=input_path,
        )
        with self._lock:
            self._jobs[job.id] = job
        if self._worker is None:
            self._run_and_store(job.id)
        else:
            self._queue.put(job.id)
        return asdict(job)

    def wait_for_job(self, job_id: str, *, timeout_seconds: float = 30) -> dict[str, Any]:
        import time

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            job = self.get_job(job_id)
            if job is not None and job["status"] in {"succeeded", "failed"}:
                return job
            time.sleep(0.05)
        raise TimeoutError(f"job did not finish: {job_id}")

    def read_repo_file(self, path: str, *, max_bytes: int = 262_144) -> dict[str, Any]:
        resolved = self._resolve_repo_file(path)
        data = resolved.read_bytes()
        truncated = len(data) > max_bytes
        text = data[:max_bytes].decode("utf-8", errors="replace")
        return {
            "path": self._display_path(resolved),
            "size_bytes": len(data),
            "truncated": truncated,
            "text": text,
        }

    def _candidate_summary(self, path: Path, source_kind: str) -> dict[str, Any]:
        try:
            candidate = load_candidate(path)
            candidate_id = str(candidate.get("candidate_id", path.stem))
            operators = candidate.get("operators", {})
            l_matrix = operators.get("L", {"rows": []})
            p_matrix = operators.get("P", {"rows": []})
            rows = l_matrix.get("rows", []) if isinstance(l_matrix, dict) else []
            artifact_status = self._artifact_status(candidate_id)
            errors = validate_candidate(candidate, self.repo_root)
            return {
                "candidate_id": candidate_id,
                "source_kind": source_kind,
                "path": self._display_path(path),
                "fields": candidate.get("fields", []),
                "claims": [claim.get("type") for claim in candidate.get("claims", []) if isinstance(claim, dict)],
                "matrix_size": len(rows),
                "l_bound": self._safe_matrix_bound(l_matrix),
                "p_bound": self._safe_matrix_bound(p_matrix),
                "laxforge_version": candidate.get("laxforge_version"),
                "schema_version": candidate.get("schema_version"),
                "validation_status": "schema_valid" if not errors else "schema_invalid",
                "validation_error_count": len(errors),
                "artifact_status": artifact_status.get("status"),
                "artifact_timestamp_utc": artifact_status.get("timestamp_utc"),
            }
        except Exception as exc:
            return {
                "candidate_id": path.stem,
                "source_kind": source_kind,
                "path": self._display_path(path),
                "validation_status": "unreadable",
                "validation_error_count": 1,
                "error": str(exc),
            }

    def _artifact_status(self, candidate_id: str) -> dict[str, Any]:
        status_path = self.repo_root / "artifacts" / candidate_id / "proof-status.json"
        if not status_path.is_file():
            return {}
        try:
            return json.loads(status_path.read_text(encoding="utf-8"))
        except Exception:
            return {"status": "unreadable"}

    def _worker_loop(self) -> None:
        while True:
            job_id = self._queue.get()
            if job_id is None:
                return
            self._run_and_store(job_id)

    def _run_and_store(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "running"
            job.started_at = utc_timestamp()
            job.log.append(f"[{job.started_at}] started {job.label}")
        try:
            result, log, ok = self._run_job(job)
            with self._lock:
                job.result = result
                job.log.extend(log)
                job.exit_code = 0 if ok else 1
                job.status = "succeeded" if ok else "failed"
                job.finished_at = utc_timestamp()
                job.log.append(f"[{job.finished_at}] finished with {job.status}")
        except Exception as exc:
            with self._lock:
                job.result = {"error": str(exc)}
                job.log.append(str(exc))
                job.exit_code = 1
                job.status = "failed"
                job.finished_at = utc_timestamp()

    def _run_job(self, job: ConsoleJob) -> tuple[dict[str, Any], list[str], bool]:
        if job.command == "validate_candidate":
            path = self._resolve_candidate_input_path(job.input_path)
            resolved = resolve_candidate_input(path)
            candidate = load_candidate(resolved.candidate_path)
            errors = validate_candidate(candidate, self.repo_root)
            status = "schema_valid" if not errors else "schema_invalid"
            return (
                {
                    "status": status,
                    "candidate_id": candidate.get("candidate_id", resolved.candidate_path.stem),
                    "candidate_source": resolved.metadata(),
                    "errors": errors,
                },
                [f"resolved input: {resolved.candidate_path}", f"validation status: {status}"],
                not errors,
            )

        if job.command in {"certify_candidate", "certify_expected_failure"}:
            path = self._resolve_candidate_input_path(job.input_path)
            result = certify_candidate_input(path, self.repo_root)
            result_doc = {
                "candidate_id": result.candidate_id,
                "status": result.status,
                "candidate_hash": result.candidate_hash,
                "generated_lean_hash": result.generated_lean_hash,
                "lean_file": str(result.lean_file) if result.lean_file is not None else None,
                "residual_witness": result.residual_witness,
            }
            ok = result.status == "proof_succeeded"
            if job.command == "certify_expected_failure":
                ok = result.status != "proof_succeeded"
            log = [
                f"candidate: {result.candidate_id}",
                f"proof status: {result.status}",
            ]
            if result.build_log:
                log.extend(result.build_log.splitlines()[-80:])
            return result_doc, log, ok

        if job.command == "lake_build":
            ok, log = run_lake_build("LaxCert", self.repo_root / "lean")
            return {"status": "passed" if ok else "failed"}, log.splitlines(), ok

        if job.command == "pytest":
            proc = subprocess.run(
                ["pytest", "-q"],
                cwd=str(self.repo_root),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                env=self._command_env(),
            )
            return (
                {"status": "passed" if proc.returncode == 0 else "failed"},
                proc.stdout.splitlines(),
                proc.returncode == 0,
            )

        raise ValueError(f"unsupported command: {job.command}")

    def _resolve_candidate_input_path(self, input_path: str | None) -> Path:
        if not input_path:
            raise ValueError("input path is required")
        raw = Path(input_path).expanduser()
        path = raw if raw.is_absolute() else self.repo_root / raw
        resolved = path.resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"candidate input does not exist: {input_path}")
        return resolved

    def _resolve_repo_file(self, path: str) -> Path:
        raw = Path(path)
        resolved = (raw if raw.is_absolute() else self.repo_root / raw).resolve()
        try:
            resolved.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError("file reads are restricted to the LAXCERT repository") from exc
        if not resolved.is_file():
            raise FileNotFoundError(f"file does not exist: {path}")
        return resolved

    def _display_path(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.repo_root).as_posix()
        except ValueError:
            return str(path)

    def _safe_matrix_bound(self, matrix_json: Any) -> int | None:
        try:
            if isinstance(matrix_json, dict):
                return matrix_bound(matrix_json)
        except Exception:
            return None
        return None

    def _safe_toolchain(self) -> str:
        try:
            return lean_toolchain(self.repo_root)
        except Exception:
            return "unknown"

    def _safe_mathlib_revision(self) -> str:
        try:
            return mathlib_revision(self.repo_root)
        except Exception:
            return "unknown"

    def _command_env(self) -> dict[str, str]:
        env = os.environ.copy()
        if os.name == "nt":
            env.setdefault("ELAN_HOME", "F:\\_codex\\elan")
            env["PATH"] = f"{env['ELAN_HOME']}\\bin;C:\\Users\\jamie\\.elan\\bin;" + env.get("PATH", "")
        return env


class LaxCertConsoleServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], repo_root: Path) -> None:
        super().__init__(server_address, ConsoleRequestHandler)
        self.backend = ConsoleBackend(repo_root)


class ConsoleRequestHandler(BaseHTTPRequestHandler):
    server: LaxCertConsoleServer

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/summary":
                self._send_json(self.server.backend.summary())
                return
            if parsed.path == "/api/candidates":
                self._send_json({"candidates": self.server.backend.list_candidates()})
                return
            if parsed.path == "/api/artifacts":
                self._send_json({"artifacts": self.server.backend.list_artifacts()})
                return
            if parsed.path == "/api/jobs":
                self._send_json({"jobs": self.server.backend.list_jobs()})
                return
            if parsed.path == "/api/commands":
                self._send_json({"commands": self.server.backend.command_specs()})
                return
            if parsed.path == "/api/file":
                query = parse_qs(parsed.query)
                target = query.get("path", [""])[0]
                self._send_json(self.server.backend.read_repo_file(target))
                return
            self._send_static(parsed.path)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/jobs":
                body = self._read_json_body()
                job = self.server.backend.submit_job(
                    str(body.get("command", "")),
                    body.get("input_path"),
                )
                self._send_json({"job": job}, status=202)
                return
            self._send_json({"error": "not found"}, status=404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)

    def _read_json_body(self) -> dict[str, Any]:
        size = int(self.headers.get("Content-Length", "0"))
        if size == 0:
            return {}
        return json.loads(self.rfile.read(size).decode("utf-8"))

    def _send_json(self, data: dict[str, Any], *, status: int = 200) -> None:
        payload = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_static(self, request_path: str) -> None:
        name = "index.html" if request_path in {"/", "/console", "/console/"} else request_path.lstrip("/")
        if "/" in name or "\\" in name:
            self._send_json({"error": "not found"}, status=404)
            return
        static_root = files("laxforge_laxcert").joinpath("console_static")
        target = static_root.joinpath(name)
        if not target.is_file():
            self._send_json({"error": "not found"}, status=404)
            return
        data = target.read_bytes()
        content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        if name.endswith(".js"):
            content_type = "text/javascript"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local LAXCERT visual console.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = LaxCertConsoleServer((args.host, args.port), args.repo_root)
    url = f"http://{args.host}:{server.server_port}"
    print(f"LAXCERT console listening on {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.backend.close()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
