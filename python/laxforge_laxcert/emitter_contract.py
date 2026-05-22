"""Deterministic LAXCERT candidate normalizer, Lean emitter, and build wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any, Literal
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess

from jsonschema import Draft202012Validator

ProofStatus = Literal[
    "schema_invalid",
    "unsupported_expression",
    "emission_failed",
    "lean_elaboration_failed",
    "proof_succeeded",
    "proof_failed_nonzero_residual",
]

Jet = tuple[str, int]
Monomial = tuple[tuple[Jet, int], ...]
Poly = dict[Monomial, Fraction]
DiffOp = dict[int, Poly]
MatrixOp = list[list[DiffOp]]

ZERO_MONOMIAL: Monomial = ()
LAXCERT_VERSION = "0.1.0"


@dataclass(frozen=True)
class LaxCertBuildResult:
    candidate_id: str
    status: ProofStatus
    candidate_hash: str
    generated_lean_hash: str | None
    lean_file: Path | None
    build_log: str
    residual_witness: dict[str, Any] | None = None


@dataclass(frozen=True)
class CandidateInput:
    candidate_path: Path
    source_kind: Literal["candidate_json", "laxforge_artifact_dir", "laxforge_manifest"]
    source_path: Path
    manifest_path: Path | None = None
    manifest_hash: str | None = None

    def metadata(self) -> dict[str, Any]:
        doc: dict[str, Any] = {
            "source_kind": self.source_kind,
            "source_path": str(self.source_path),
            "candidate_path": str(self.candidate_path),
        }
        if self.manifest_path is not None:
            doc["manifest_path"] = str(self.manifest_path)
        if self.manifest_hash is not None:
            doc["manifest_hash"] = self.manifest_hash
        return doc


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relative_artifact_uri(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def lean_toolchain(repo_root: Path) -> str:
    return (repo_root / "lean" / "lean-toolchain").read_text(encoding="utf-8").strip()


def mathlib_revision(repo_root: Path) -> str:
    manifest_path = repo_root / "lean" / "lake-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for package in manifest.get("packages", []):
            if package.get("name") == "mathlib" and package.get("rev"):
                return f"git:{package['rev']}"
    except Exception:
        pass
    return "unknown"


def ledger_base(
    *,
    candidate: dict[str, Any],
    candidate_id: str,
    candidate_hash: str,
    repo_root: Path,
    artifact_dir: Path,
    status: ProofStatus,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "candidate_hash": candidate_hash,
        "status": status,
        "schema_version": candidate.get("schema_version"),
        "laxcert_schema_version": candidate.get("laxcert_schema_version"),
        "laxforge_version": candidate.get("laxforge_version", "unknown"),
        "laxcert_version": f"laxcert:{LAXCERT_VERSION}",
        "lean_toolchain": lean_toolchain(repo_root),
        "mathlib_revision": mathlib_revision(repo_root),
        "timestamp_utc": utc_timestamp(),
        "build_log_uri": relative_artifact_uri(repo_root, artifact_dir / "lake-build.log"),
    }


def load_candidate(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def looks_like_candidate_json(data: dict[str, Any]) -> bool:
    return {"candidate_id", "operators", "evolution", "claims"} <= data.keys()


def candidate_path_from_manifest(manifest_path: Path) -> Path:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate_rel = (
        manifest.get("candidate_json")
        or manifest.get("candidate_path")
        or manifest.get("laxcert_candidate_json")
    )
    if not isinstance(candidate_rel, str) or not candidate_rel:
        raise ValueError(f"LAXFORGE manifest {manifest_path} must declare candidate_json")
    candidate_path = (manifest_path.parent / candidate_rel).resolve()
    if not candidate_path.is_file():
        raise FileNotFoundError(f"LAXFORGE manifest candidate_json does not exist: {candidate_path}")
    return candidate_path


def resolve_candidate_input(input_path: Path) -> CandidateInput:
    path = input_path.resolve()
    if path.is_dir():
        manifest_path = path / "laxforge_manifest.json"
        if manifest_path.is_file():
            manifest_text = manifest_path.read_text(encoding="utf-8")
            return CandidateInput(
                candidate_path=candidate_path_from_manifest(manifest_path),
                source_kind="laxforge_artifact_dir",
                source_path=path,
                manifest_path=manifest_path,
                manifest_hash=sha256_text(manifest_text),
            )
        for name in ("candidate.json", "laxcert_candidate.json", "laxforge_candidate.json"):
            candidate_path = path / name
            if candidate_path.is_file():
                return CandidateInput(
                    candidate_path=candidate_path.resolve(),
                    source_kind="laxforge_artifact_dir",
                    source_path=path,
                )
        raise FileNotFoundError(f"No candidate JSON or laxforge_manifest.json found in {path}")

    if not path.is_file():
        raise FileNotFoundError(f"Candidate input does not exist: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if looks_like_candidate_json(data):
        return CandidateInput(
            candidate_path=path,
            source_kind="candidate_json",
            source_path=path,
        )
    candidate_path = candidate_path_from_manifest(path)
    return CandidateInput(
        candidate_path=candidate_path,
        source_kind="laxforge_manifest",
        source_path=path,
        manifest_path=path,
        manifest_hash=sha256_text(path.read_text(encoding="utf-8")),
    )


def load_schema(repo_root: Path) -> dict[str, Any]:
    return json.loads((repo_root / "schemas" / "laxcert_candidate.schema.json").read_text(encoding="utf-8"))


def _path(parts: list[str | int]) -> str:
    return "/".join(str(part) for part in parts)


def _iter_scalar_exprs(expr: Any, path: list[str | int]):
    if not isinstance(expr, dict):
        return
    yield path, expr
    kind = expr.get("kind")
    if kind in {"add", "mul"}:
        for idx, arg in enumerate(expr.get("args", [])):
            yield from _iter_scalar_exprs(arg, [*path, "args", idx])
    elif kind == "neg":
        yield from _iter_scalar_exprs(expr.get("arg"), [*path, "arg"])
    elif kind == "pow":
        yield from _iter_scalar_exprs(expr.get("base"), [*path, "base"])


def _iter_matrix_diffops(matrix: Any, path: list[str | int]):
    if not isinstance(matrix, dict):
        return
    rows = matrix.get("rows")
    if not isinstance(rows, list):
        return
    for i, row in enumerate(rows):
        if not isinstance(row, list):
            continue
        for j, diffop in enumerate(row):
            yield [*path, "rows", i, j], diffop


def _validate_matrix_shape(matrix: Any, path: list[str | int], errors: list[str]) -> tuple[int, int] | None:
    if not isinstance(matrix, dict):
        return None
    rows = matrix.get("rows")
    if not isinstance(rows, list) or not rows:
        return None
    if not all(isinstance(row, list) for row in rows):
        return None
    width = len(rows[0])
    if width == 0:
        errors.append(f"{_path([*path, 'rows'])}: matrix rows must be nonempty")
        return None
    for idx, row in enumerate(rows):
        if len(row) != width:
            errors.append(f"{_path([*path, 'rows', idx])}: matrix rows must be rectangular")
    if len(rows) != width:
        errors.append(f"{_path([*path, 'rows'])}: matrix must be square for generated certificates")
    return len(rows), width


def _semantic_validation_errors(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declared_fields = {field for field in candidate.get("fields", []) if isinstance(field, str)}

    schema_version = candidate.get("schema_version")
    laxcert_schema_version = candidate.get("laxcert_schema_version")
    if schema_version and laxcert_schema_version and schema_version != laxcert_schema_version:
        errors.append("schema_version must match laxcert_schema_version")

    evolution = candidate.get("evolution", {})
    if declared_fields and isinstance(evolution, dict):
        evolution_fields = set(evolution.keys())
        if evolution_fields != declared_fields:
            errors.append(f"evolution fields {sorted(evolution_fields)} must match fields {sorted(declared_fields)}")
        for field, expr in evolution.items():
            for expr_path, scalar in _iter_scalar_exprs(expr, ["evolution", field]):
                if scalar.get("kind") == "jet" and scalar.get("field") not in declared_fields:
                    errors.append(f"{_path(expr_path)}: jet field {scalar.get('field')!r} is not declared")

    ops = candidate.get("operators", {})
    if isinstance(ops, dict):
        shapes: dict[str, tuple[int, int]] = {}
        for op_name in ("L", "P", "U", "V"):
            if op_name not in ops:
                continue
            shape = _validate_matrix_shape(ops[op_name], ["operators", op_name], errors)
            if shape is not None:
                shapes[op_name] = shape

            if op_name in {"L", "P"}:
                for diffop_path, diffop in _iter_matrix_diffops(ops[op_name], ["operators", op_name]):
                    if not isinstance(diffop, dict) or not isinstance(diffop.get("terms"), list):
                        continue
                    seen_orders: set[int] = set()
                    for term_idx, term in enumerate(diffop["terms"]):
                        if not isinstance(term, dict):
                            continue
                        order = term.get("order")
                        if isinstance(order, int):
                            if order in seen_orders:
                                errors.append(f"{_path([*diffop_path, 'terms', term_idx])}: duplicate differential order {order}")
                            seen_orders.add(order)
                        coeff = term.get("coeff")
                        for expr_path, scalar in _iter_scalar_exprs(coeff, [*diffop_path, "terms", term_idx, "coeff"]):
                            if scalar.get("kind") == "jet" and scalar.get("field") not in declared_fields:
                                errors.append(f"{_path(expr_path)}: jet field {scalar.get('field')!r} is not declared")

        if "L" in shapes and "P" in shapes and shapes["L"] != shapes["P"]:
            errors.append("operators L and P must have the same matrix shape")
        if "U" in shapes and "V" in shapes and shapes["U"] != shapes["V"]:
            errors.append("operators U and V must have the same matrix shape")

    return errors


def validate_candidate(candidate: dict[str, Any], repo_root: Path) -> list[str]:
    validator = Draft202012Validator(load_schema(repo_root))
    errors = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in sorted(validator.iter_errors(candidate), key=str)]
    errors.extend(_semantic_validation_errors(candidate))
    return errors


def frac(value: Any) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict) and {"num", "den"} <= value.keys():
        return Fraction(int(value["num"]), int(value["den"]))
    raise ValueError(f"unsupported rational constant: {value!r}")


def clean(poly: Poly) -> Poly:
    return {m: c for m, c in poly.items() if c}


def poly_const(value: Fraction) -> Poly:
    return clean({ZERO_MONOMIAL: value})


def poly_jet(field: str, order: int) -> Poly:
    return {(((field, order), 1),): Fraction(1)}


def poly_add(a: Poly, b: Poly) -> Poly:
    out = dict(a)
    for m, c in b.items():
        out[m] = out.get(m, Fraction(0)) + c
    return clean(out)


def poly_neg(a: Poly) -> Poly:
    return {m: -c for m, c in a.items()}


def poly_sub(a: Poly, b: Poly) -> Poly:
    return poly_add(a, poly_neg(b))


def merge_monomials(a: Monomial, b: Monomial) -> Monomial:
    powers: dict[Jet, int] = {}
    for jet, exp in a + b:
        powers[jet] = powers.get(jet, 0) + exp
    return tuple(sorted((jet, exp) for jet, exp in powers.items() if exp))


def poly_mul(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            m = merge_monomials(ma, mb)
            out[m] = out.get(m, Fraction(0)) + ca * cb
    return clean(out)


def poly_pow(a: Poly, n: int) -> Poly:
    out = poly_const(Fraction(1))
    for _ in range(n):
        out = poly_mul(out, a)
    return out


def monomial_dx(monomial: Monomial) -> Poly:
    out: Poly = {}
    for jet, exp in monomial:
        if exp == 0:
            continue
        field, order = jet
        powers = dict(monomial)
        powers[jet] -= 1
        if powers[jet] == 0:
            del powers[jet]
        shifted = (field, order + 1)
        powers[shifted] = powers.get(shifted, 0) + 1
        new_m = tuple(sorted((j, e) for j, e in powers.items() if e))
        out[new_m] = out.get(new_m, Fraction(0)) + exp
    return clean(out)


def poly_dx(a: Poly) -> Poly:
    out: Poly = {}
    for m, c in a.items():
        out = poly_add(out, {mm: c * cc for mm, cc in monomial_dx(m).items()})
    return clean(out)


def poly_dx_n(a: Poly, n: int) -> Poly:
    out = a
    for _ in range(n):
        out = poly_dx(out)
    return out


def monomial_dt(monomial: Monomial, evolution: dict[str, Poly]) -> Poly:
    out: Poly = {}
    for jet, exp in monomial:
        field, order = jet
        replacement = poly_dx_n(evolution[field], order)
        if exp > 1:
            replacement = poly_mul(poly_const(Fraction(exp)), poly_mul(poly_pow(poly_jet(field, order), exp - 1), replacement))
        powers = dict(monomial)
        powers[jet] -= exp
        if powers.get(jet) == 0:
            powers.pop(jet, None)
        rest = {tuple(sorted((j, e) for j, e in powers.items() if e)): Fraction(1)}
        out = poly_add(out, poly_mul(rest, replacement))
    return clean(out)


def poly_dt(a: Poly, evolution: dict[str, Poly]) -> Poly:
    out: Poly = {}
    for m, c in a.items():
        out = poly_add(out, {mm: c * cc for mm, cc in monomial_dt(m, evolution).items()})
    return clean(out)


def expr_to_poly(expr: dict[str, Any]) -> Poly:
    kind = expr["kind"]
    if kind == "const":
        return poly_const(frac(expr["value"]))
    if kind == "jet":
        return poly_jet(expr["field"], int(expr["order"]))
    if kind == "add":
        out: Poly = {}
        for arg in expr["args"]:
            out = poly_add(out, expr_to_poly(arg))
        return out
    if kind == "mul":
        out = poly_const(Fraction(1))
        for arg in expr["args"]:
            out = poly_mul(out, expr_to_poly(arg))
        return out
    if kind == "neg":
        return poly_neg(expr_to_poly(expr["arg"]))
    if kind == "pow":
        return poly_pow(expr_to_poly(expr["base"]), int(expr["exponent"]))
    raise ValueError(f"unsupported expression kind: {kind}")


def diffop_from_json(data: dict[str, Any]) -> DiffOp:
    out: DiffOp = {}
    seen: set[int] = set()
    for term in data["terms"]:
        order = int(term["order"])
        if order in seen:
            raise ValueError(f"duplicate differential order {order}")
        seen.add(order)
        out[order] = poly_add(out.get(order, {}), expr_to_poly(term["coeff"]))
    return {k: v for k, v in out.items() if v}


def matrix_from_json(data: dict[str, Any]) -> MatrixOp:
    rows = data["rows"]
    width = len(rows[0]) if rows else 0
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("matrix rows must be rectangular and nonempty")
    return [[diffop_from_json(cell) for cell in row] for row in rows]


def op_add(a: DiffOp, b: DiffOp) -> DiffOp:
    out = dict(a)
    for order, coeff in b.items():
        out[order] = poly_add(out.get(order, {}), coeff)
    return {k: v for k, v in out.items() if v}


def op_neg(a: DiffOp) -> DiffOp:
    return {order: poly_neg(coeff) for order, coeff in a.items()}


def op_sub(a: DiffOp, b: DiffOp) -> DiffOp:
    return op_add(a, op_neg(b))


def op_compose(a: DiffOp, b: DiffOp) -> DiffOp:
    out: DiffOp = {}
    for m, ca in a.items():
        for n, cb in b.items():
            for j in range(m + 1):
                order = m - j + n
                coeff = poly_mul(poly_mul(poly_const(Fraction(comb(m, j))), ca), poly_dx_n(cb, j))
                out[order] = poly_add(out.get(order, {}), coeff)
    return {k: v for k, v in out.items() if v}


def matrix_zero(rows: int, cols: int) -> MatrixOp:
    return [[{} for _ in range(cols)] for _ in range(rows)]


def matrix_compose(a: MatrixOp, b: MatrixOp) -> MatrixOp:
    rows, inner, cols = len(a), len(b), len(b[0])
    out = matrix_zero(rows, cols)
    for i in range(rows):
        for j in range(cols):
            cell: DiffOp = {}
            for k in range(inner):
                cell = op_add(cell, op_compose(a[i][k], b[k][j]))
            out[i][j] = cell
    return out


def matrix_sub(a: MatrixOp, b: MatrixOp) -> MatrixOp:
    return [[op_sub(a[i][j], b[i][j]) for j in range(len(a[0]))] for i in range(len(a))]


def matrix_dt(a: MatrixOp, evolution: dict[str, Poly]) -> MatrixOp:
    return [[{order: poly_dt(coeff, evolution) for order, coeff in cell.items()} for cell in row] for row in a]


def commutator(a: MatrixOp, b: MatrixOp) -> MatrixOp:
    return matrix_sub(matrix_compose(a, b), matrix_compose(b, a))


def op_adjoint(a: DiffOp) -> DiffOp:
    out: DiffOp = {}
    for k, coeff in a.items():
        sign = Fraction(-1 if k % 2 else 1)
        for j in range(k + 1):
            order = k - j
            term = poly_mul(poly_const(sign * comb(k, j)), poly_dx_n(coeff, j))
            out[order] = poly_add(out.get(order, {}), term)
    return {order: coeff for order, coeff in out.items() if coeff}


def matrix_adjoint(a: MatrixOp) -> MatrixOp:
    rows, cols = len(a), len(a[0])
    return [[op_adjoint(a[j][i]) for j in range(rows)] for i in range(cols)]


def matrix_neg(a: MatrixOp) -> MatrixOp:
    return [[op_neg(cell) for cell in row] for row in a]


def lax_residual(candidate: dict[str, Any]) -> MatrixOp:
    ops = candidate["operators"]
    l = matrix_from_json(ops["L"])
    p = matrix_from_json(ops["P"])
    evolution = {field: expr_to_poly(expr) for field, expr in candidate["evolution"].items()}
    return matrix_sub(matrix_dt(l, evolution), commutator(p, l))


def matrix_witness(matrix: MatrixOp, status: str) -> dict[str, Any] | None:
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            for order, coeff in sorted(cell.items()):
                if coeff:
                    return {
                        "status": status,
                        "entry": [i, j],
                        "operator_order": order,
                        "residual_display": poly_display(coeff),
                    }
    return None


def claim_witness(candidate: dict[str, Any]) -> dict[str, Any] | None:
    ops = candidate["operators"]
    l = matrix_from_json(ops["L"])
    p = matrix_from_json(ops["P"])
    for claim in candidate["claims"]:
        claim_type = claim["type"]
        if claim_type == "lax_equation":
            witness = matrix_witness(lax_residual(candidate), "failed_nonzero_residual")
            if witness:
                witness["claim_type"] = claim_type
                return witness
        elif claim_type == "self_adjoint_L":
            witness = matrix_witness(matrix_sub(matrix_adjoint(l), l), "failed_self_adjoint")
            if witness:
                witness["claim_type"] = claim_type
                return witness
        elif claim_type == "skew_adjoint_P":
            witness = matrix_witness(matrix_sub(matrix_adjoint(p), matrix_neg(p)), "failed_skew_adjoint")
            if witness:
                witness["claim_type"] = claim_type
                return witness
        elif claim_type in {"zero_curvature", "gauge_equivalence"}:
            return {"status": "unsupported_claim", "claim_type": claim_type}
    return None


def poly_display(poly: Poly) -> str:
    if not poly:
        return "0"
    parts: list[str] = []
    for monomial, coeff in sorted(poly.items(), key=lambda item: repr(item[0])):
        vars_part = "*".join(f"{field}_{order}^{exp}" for ((field, order), exp) in monomial)
        coeff_part = str(coeff)
        parts.append(coeff_part if not vars_part else f"{coeff_part}*{vars_part}")
    return " + ".join(parts)


def residual_witness(residual: MatrixOp) -> dict[str, Any] | None:
    for i, row in enumerate(residual):
        for j, cell in enumerate(row):
            for order, coeff in sorted(cell.items()):
                if coeff:
                    return {
                        "status": "failed_nonzero_residual",
                        "entry": [i, j],
                        "operator_order": order,
                        "residual_display": poly_display(coeff),
                    }
    return None


def lean_module_name(candidate_id: str) -> str:
    parts = re.sub(r"[^A-Za-z0-9_]", "_", candidate_id).split("_")
    name = "".join(part[:1].upper() + part[1:] for part in parts if part)
    if not name or name[0].isdigit():
        name = "Candidate" + name
    return name


def lean_rat(value: Any) -> str:
    f = frac(value)
    if f.denominator == 1:
        return f"({f.numerator} : Rat)"
    return f"({f.numerator} / {f.denominator} : Rat)"


def lean_scalar_expr(expr: dict[str, Any]) -> str:
    kind = expr["kind"]
    if kind == "const":
        value = frac(expr["value"])
        if value == 0:
            return "ScalarExpr.zero"
        if value == 1:
            return "ScalarExpr.one"
        return f"ScalarExpr.const {lean_rat(expr['value'])}"
    if kind == "jet":
        return f"ScalarExpr.jetDx .{expr['field']} {int(expr['order'])}"
    if kind == "add":
        args = [lean_scalar_expr(arg) for arg in expr["args"]]
        out = args[0]
        for arg in args[1:]:
            out = f"ScalarExpr.mkAdd ({out}) ({arg})"
        return out
    if kind == "mul":
        args = [lean_scalar_expr(arg) for arg in expr["args"]]
        out = args[0]
        for arg in args[1:]:
            out = f"ScalarExpr.mkMul ({out}) ({arg})"
        return out
    if kind == "neg":
        return f"ScalarExpr.mkNeg ({lean_scalar_expr(expr['arg'])})"
    if kind == "pow":
        return f"ScalarExpr.pow ({lean_scalar_expr(expr['base'])}) {int(expr['exponent'])}"
    raise ValueError(f"unsupported expression kind for Lean emission: {kind}")


def op_bound(op_json: dict[str, Any]) -> int:
    return max((int(term["order"]) for term in op_json["terms"]), default=0)


def matrix_bound(matrix_json: dict[str, Any]) -> int:
    return max((op_bound(cell) for row in matrix_json["rows"] for cell in row), default=0)


def if_chain_fin(var_name: str, values: list[str]) -> str:
    if not values:
        raise ValueError("if_chain_fin requires at least one value")
    if len(values) == 1:
        return values[0]
    out = values[-1]
    for idx in range(len(values) - 2, -1, -1):
        out = f"if {var_name}.val = {idx} then {values[idx]} else {out}"
    return out


def if_chain_nat(var_name: str, values: list[str]) -> str:
    if not values:
        raise ValueError("if_chain_nat requires at least one value")
    if len(values) == 1:
        return values[0]
    out = values[-1]
    for idx in range(len(values) - 2, -1, -1):
        out = f"if {var_name} = {idx} then {values[idx]} else {out}"
    return out


def lean_diffop(op_json: dict[str, Any], bound: int) -> str:
    coeffs = {int(term["order"]): term["coeff"] for term in op_json["terms"]}
    unsupported = sorted(order for order in coeffs if order > bound)
    if unsupported:
        raise ValueError(f"operator has orders above declared bound {bound}: {unsupported}")
    values = [
        lean_scalar_expr(coeffs.get(order, {"kind": "const", "value": 0}))
        for order in range(bound + 1)
    ]
    return f"BoundedDiffOp.ofCoeffs {bound} (fun k => {if_chain_nat('k', values)})"


def fin_lit(value: int, size: int) -> str:
    return f"(⟨{value}, by decide⟩ : Fin {size})"


def matrix_accessor(name: str, i: int, j: int, n: int) -> str:
    return f"({name} {fin_lit(i, n)} {fin_lit(j, n)})"


def matrix_cell_name(name: str, i: int, j: int) -> str:
    return f"{name}_{i}_{j}"


def lean_matrix_def(name: str, matrix_json: dict[str, Any], bound: int) -> tuple[str, int]:
    rows = matrix_json["rows"]
    n = len(rows)
    if n == 0 or any(len(row) != n for row in rows):
        raise ValueError(f"{name} must be a nonempty square matrix for generated Lean certificates")
    blocks: list[str] = []
    cell_refs: list[list[str]] = []
    for i, row in enumerate(rows):
        cell_row: list[str] = []
        for j, cell in enumerate(row):
            cell_name = matrix_cell_name(name, i, j)
            blocks.append(f"def {cell_name} : BoundedDiffOp ScalarExpr {bound} :=\n  {lean_diffop(cell, bound)}")
            cell_row.append(cell_name)
        cell_refs.append(cell_row)
    row_exprs = [if_chain_fin("j", row) for row in cell_refs]
    body = if_chain_fin("i", row_exprs)
    blocks.append(f"def {name} : MatrixOp {n} ScalarExpr {bound} := fun i j =>\n  {body}")
    return "\n\n".join(blocks), n


def lean_evolution(candidate: dict[str, Any]) -> str:
    cases = []
    for field in ["u", "p", "q"]:
        if field in candidate["evolution"]:
            cases.append(f"  | .{field} => {lean_scalar_expr(candidate['evolution'][field])}")
        else:
            cases.append(f"  | .{field} => ScalarExpr.zero")
    return "def evolution : ScalarExpr.Evolution := fun field =>\n  match field with\n" + "\n".join(cases)


def compose_sum(left: str, right: str, i: int, j: int, n: int, out_bound: int) -> str:
    terms = [
        f"BoundedDiffOp.composeToBound {out_bound} {matrix_accessor(left, i, k, n)} {matrix_accessor(right, k, j, n)}"
        for k in range(n)
    ]
    out = terms[0]
    for term in terms[1:]:
        out = f"({out}) + ({term})"
    return out


def residual_cell(i: int, j: int, n: int, out_bound: int) -> str:
    dt = f"dtOp {matrix_accessor('L', i, j, n)}"
    pl = compose_sum("P", "L", i, j, n, out_bound)
    lp = compose_sum("L", "P", i, j, n, out_bound)
    return f"({dt}) - (({pl}) - ({lp}))"


def lean_matrix_from_cells(name: str, n: int, order: int, cells: list[list[str]]) -> str:
    blocks: list[str] = []
    cell_refs: list[list[str]] = []
    for i, row in enumerate(cells):
        cell_row: list[str] = []
        for j, cell in enumerate(row):
            cell_name = matrix_cell_name(name, i, j)
            blocks.append(f"def {cell_name} : BoundedDiffOp ScalarExpr {order} :=\n  {cell}")
            cell_row.append(cell_name)
        cell_refs.append(cell_row)
    row_exprs = [if_chain_fin("j", row) for row in cell_refs]
    body = if_chain_fin("i", row_exprs)
    blocks.append(f"def {name} : MatrixOp {n} ScalarExpr {order} := fun i j =>\n  {body}")
    return "\n\n".join(blocks)


def fin_value_disjunction(var_name: str, size: int) -> str:
    return " ∨ ".join(f"{var_name}.val = {idx}" for idx in range(size))


def emit_fin_index_proof(n: int, order: int, matrix_name: str) -> str:
    k_size = order + 1
    if n <= 0 or k_size <= 0:
        raise ValueError("finite index proof sizes must be positive")

    lines = [
        "  intro i j k",
        f"  have h_i : {fin_value_disjunction('i', n)} := by omega",
    ]
    if n > 1:
        lines.extend([
            f"  rcases h_i with {' | '.join(['h_i'] * n)} <;>",
            f"    have h_j : {fin_value_disjunction('j', n)} := by omega",
        ])
    else:
        lines.append(f"  have h_j : {fin_value_disjunction('j', n)} := by omega")

    if n > 1:
        lines.extend([
            "  all_goals",
            f"    rcases h_j with {' | '.join(['h_j'] * n)} <;>",
            f"      have h_k : {fin_value_disjunction('k', k_size)} := by omega",
        ])
    else:
        lines.append(f"  have h_k : {fin_value_disjunction('k', k_size)} := by omega")

    if k_size > 1:
        lines.extend([
            "  all_goals",
            f"    rcases h_k with {' | '.join(['h_k'] * k_size)} <;>",
            f"      simp only [{matrix_name}, h_i, h_j]",
        ])
    else:
        lines.extend([
            "  all_goals",
            f"    simp only [{matrix_name}, h_i, h_j]",
        ])

    lines.extend([
        "  all_goals",
        "    first",
    ])
    for idx in range(k_size):
        lines.append(
            f"      | have h_k_eq : k = {fin_lit(idx, k_size)} := by apply Fin.ext; assumption"
        )
    lines.extend([
        "    subst k",
        "    native_decide",
    ])
    return "\n".join(lines)


def emit_indexed_coefficient_certificate(
    *,
    at_name: str,
    certificate_name: str,
    indexed_theorem_name: str,
    candidate_theorem_name: str,
    matrix_name: str,
    n: int,
    order: int,
) -> str:
    coefficient_prop = f"ScalarExpr.simplify ((({matrix_name} i j).coeff k)) = ScalarExpr.zero"
    return "\n\n".join(
        [
            (
                f"def {at_name} (i : Fin {n}) (j : Fin {n}) (k : Fin {order + 1}) : Prop :=\n"
                f"  {coefficient_prop}"
            ),
            f"def {certificate_name} : Prop :=\n  ∀ i j k, {coefficient_prop}",
            (
                f"theorem {indexed_theorem_name} :\n"
                f"    ∀ i j k, {coefficient_prop} := by\n"
                f"{emit_fin_index_proof(n, order, matrix_name)}"
            ),
            f"theorem {candidate_theorem_name} : {certificate_name} := by\n  exact {indexed_theorem_name}",
        ]
    )


def emit_lean_certificate(candidate: dict[str, Any]) -> str:
    module_name = lean_module_name(candidate["candidate_id"])
    l_bound = matrix_bound(candidate["operators"]["L"])
    p_bound = matrix_bound(candidate["operators"]["P"])
    residual_bound = l_bound + p_bound
    l_def, n = lean_matrix_def("L", candidate["operators"]["L"], l_bound)
    p_def, p_n = lean_matrix_def("P", candidate["operators"]["P"], p_bound)
    if n != p_n:
        raise ValueError("L and P dimensions differ")

    residual_cells = [[residual_cell(i, j, n, residual_bound) for j in range(n)] for i in range(n)]
    residual_def = lean_matrix_from_cells("laxResidual", n, residual_bound, residual_cells)
    theorem_blocks = [
        emit_indexed_coefficient_certificate(
            at_name="laxCoefficientAt",
            certificate_name="laxCoefficientCertificate",
            indexed_theorem_name="laxCoefficientCertificate_indexed",
            candidate_theorem_name="candidate_satisfies_lax_equation",
            matrix_name="laxResidual",
            n=n,
            order=residual_bound,
        ),
    ]

    if any(claim["type"] == "self_adjoint_L" for claim in candidate["claims"]):
        cells = [
            [
                f"BoundedDiffOp.formalAdjointBounded {matrix_accessor('L', j, i, n)} - {matrix_accessor('L', i, j, n)}"
                for j in range(n)
            ]
            for i in range(n)
        ]
        theorem_blocks.append(lean_matrix_from_cells("selfAdjointResidualL", n, l_bound, cells))
        theorem_blocks.append(
            emit_indexed_coefficient_certificate(
                at_name="selfAdjointLCoefficientAt",
                certificate_name="selfAdjointLCoefficientCertificate",
                indexed_theorem_name="selfAdjointLCoefficientCertificate_indexed",
                candidate_theorem_name="candidate_self_adjoint_L",
                matrix_name="selfAdjointResidualL",
                n=n,
                order=l_bound,
            )
        )

    if any(claim["type"] == "skew_adjoint_P" for claim in candidate["claims"]):
        cells = [
            [
                f"BoundedDiffOp.formalAdjointBounded {matrix_accessor('P', j, i, n)} - (-{matrix_accessor('P', i, j, n)})"
                for j in range(n)
            ]
            for i in range(n)
        ]
        theorem_blocks.append(lean_matrix_from_cells("skewAdjointResidualP", n, p_bound, cells))
        theorem_blocks.append(
            emit_indexed_coefficient_certificate(
                at_name="skewAdjointPCoefficientAt",
                certificate_name="skewAdjointPCoefficientCertificate",
                indexed_theorem_name="skewAdjointPCoefficientCertificate_indexed",
                candidate_theorem_name="candidate_skew_adjoint_P",
                matrix_name="skewAdjointResidualP",
                n=n,
                order=p_bound,
            )
        )

    body = "\n\n".join(
        [
            f"def candidateId : String := {json.dumps(candidate['candidate_id'])}",
            'def generatedBy : String := "laxforge_laxcert.emitter_contract"',
            lean_evolution(candidate),
            l_def,
            p_def,
            (
                f"def dtOp (A : BoundedDiffOp ScalarExpr {l_bound}) : BoundedDiffOp ScalarExpr {residual_bound} :=\n"
                f"  BoundedDiffOp.ofCoeffs {residual_bound} (fun k => "
                + if_chain_nat(
                    "k",
                    [
                        f"ScalarExpr.Dt evolution (BoundedDiffOp.coeffNat A {order})"
                        if order <= l_bound else "ScalarExpr.zero"
                        for order in range(residual_bound + 1)
                    ],
                )
                + ")"
            ),
            residual_def,
            *theorem_blocks,
        ]
    )
    return f"""import LaxCert

namespace LaxCert.Generated.{module_name}

{body}

end LaxCert.Generated.{module_name}
"""


def emit_lean(candidate: dict[str, Any], out_dir: Path) -> Path:
    module_name = lean_module_name(candidate["candidate_id"])
    lean_source = emit_lean_certificate(candidate)
    lean_path = out_dir / f"{module_name}.lean"
    lean_path.parent.mkdir(parents=True, exist_ok=True)
    lean_path.write_text(lean_source, encoding="utf-8")
    return lean_path


def run_lake_build(module: str, cwd: Path) -> tuple[bool, str]:
    env = os.environ.copy()
    if os.name == "nt":
        env.setdefault("ELAN_HOME", "F:\\_codex\\elan")
        env["PATH"] = f"{env['ELAN_HOME']}\\bin;C:\\Users\\jamie\\.elan\\bin;" + env.get("PATH", "")
    else:
        home = Path.home()
        env["PATH"] = f"{home / '.elan' / 'bin'}:" + env.get("PATH", "")
    proc = subprocess.run(
        ["lake", "-R", "build", module],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=env,
    )
    return proc.returncode == 0, proc.stdout


def write_artifact(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_candidate(
    candidate_path: Path,
    repo_root: Path,
    candidate_source: dict[str, Any] | None = None,
) -> LaxCertBuildResult:
    raw = candidate_path.read_text(encoding="utf-8")
    candidate_hash = sha256_text(raw)
    artifact_dir = repo_root / "artifacts" / json.loads(raw).get("candidate_id", candidate_path.stem)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_artifact(artifact_dir / "candidate.json", raw)
    if candidate_source is not None:
        write_artifact(artifact_dir / "candidate-source.json", canonical_json(candidate_source) + "\n")

    try:
        candidate = json.loads(raw)
        candidate_id = candidate.get("candidate_id", candidate_path.stem)
        errors = validate_candidate(candidate, repo_root)
        if errors:
            status: ProofStatus = "schema_invalid"
            write_artifact(artifact_dir / "lake-build.log", "\n".join(errors) + "\n")
            status_doc = ledger_base(
                candidate=candidate,
                candidate_id=candidate_id,
                candidate_hash=candidate_hash,
                repo_root=repo_root,
                artifact_dir=artifact_dir,
                status=status,
            )
            status_doc.update({
                "event_type": "laxcert.proof.failed",
                "errors": errors,
            })
            if candidate_source is not None:
                status_doc["candidate_source"] = candidate_source
            write_artifact(artifact_dir / "proof-status.json", json.dumps(status_doc, indent=2, sort_keys=True))
            return LaxCertBuildResult(candidate_id, status, candidate_hash, None, None, "\n".join(errors), None)

        witness = claim_witness(candidate)
        normalized = {
            "candidate": candidate,
            "residual_witness": witness,
        }
        normalized_text = canonical_json(normalized)
        write_artifact(artifact_dir / "candidate.normalized.json", normalized_text + "\n")

        assumptions_text = canonical_json(candidate.get("assumptions", []))
        provenance_text = canonical_json(candidate.get("provenance", {}))
        write_artifact(artifact_dir / "assumptions.json", assumptions_text + "\n")
        write_artifact(artifact_dir / "provenance.json", provenance_text + "\n")

        if witness:
            status = "proof_failed_nonzero_residual"
            write_artifact(
                artifact_dir / "lake-build.log",
                "No Lean build invoked: coefficient residual witness found before Lean emission.\n",
            )
            status_doc = ledger_base(
                candidate=candidate,
                candidate_id=candidate_id,
                candidate_hash=candidate_hash,
                repo_root=repo_root,
                artifact_dir=artifact_dir,
                status=status,
            )
            status_doc.update({
                "event_type": "laxcert.proof.failed",
                "claim_type": ",".join(claim["type"] for claim in candidate["claims"]),
                "normalized_hash": sha256_text(normalized_text),
                "assumptions_hash": sha256_text(assumptions_text),
                "residual_witness": witness,
            })
            if candidate_source is not None:
                status_doc["candidate_source"] = candidate_source
            write_artifact(artifact_dir / "proof-status.json", json.dumps(status_doc, indent=2, sort_keys=True))
            return LaxCertBuildResult(candidate_id, status, candidate_hash, None, None, "", witness)

        lean_file = emit_lean(candidate, repo_root / "lean" / "LaxCert" / "Generated")
        lean_text = lean_file.read_text(encoding="utf-8")
        lean_hash = sha256_text(lean_text)
        write_artifact(artifact_dir / "generated.lean", lean_text)
        write_artifact(artifact_dir / "generated.hash", lean_hash + "\n")

        module = "LaxCert.Generated." + lean_file.stem
        ok, log = run_lake_build(module, repo_root / "lean")
        write_artifact(artifact_dir / "lake-build.log", log)
        status = "proof_succeeded" if ok else "lean_elaboration_failed"
        status_doc = ledger_base(
            candidate=candidate,
            candidate_id=candidate_id,
            candidate_hash=candidate_hash,
            repo_root=repo_root,
            artifact_dir=artifact_dir,
            status=status,
        )
        status_doc.update({
            "event_type": "laxcert.proof.succeeded" if ok else "laxcert.proof.failed",
            "claim_type": ",".join(claim["type"] for claim in candidate["claims"]),
            "lean_theorem": f"{module}.candidate_satisfies_lax_equation",
            "normalized_hash": sha256_text(normalized_text),
            "generated_lean_hash": lean_hash,
            "lean_file": str(lean_file),
            "assumptions_hash": sha256_text(assumptions_text),
        })
        if candidate_source is not None:
            status_doc["candidate_source"] = candidate_source
        write_artifact(artifact_dir / "proof-status.json", json.dumps(status_doc, indent=2, sort_keys=True))
        return LaxCertBuildResult(candidate_id, status, candidate_hash, lean_hash, lean_file, log, None)
    except Exception as exc:
        candidate_for_ledger = json.loads(raw)
        candidate_id = candidate_for_ledger.get("candidate_id", candidate_path.stem)
        status = "emission_failed"
        write_artifact(artifact_dir / "lake-build.log", str(exc) + "\n")
        status_doc = ledger_base(
            candidate=candidate_for_ledger,
            candidate_id=candidate_id,
            candidate_hash=candidate_hash,
            repo_root=repo_root,
            artifact_dir=artifact_dir,
            status=status,
        )
        status_doc.update({
            "event_type": "laxcert.proof.failed",
            "error": str(exc),
        })
        if candidate_source is not None:
            status_doc["candidate_source"] = candidate_source
        write_artifact(artifact_dir / "proof-status.json", json.dumps(status_doc, indent=2, sort_keys=True))
        return LaxCertBuildResult(candidate_id, status, candidate_hash, None, None, str(exc), None)


def certify_candidate_input(input_path: Path, repo_root: Path) -> LaxCertBuildResult:
    resolved = resolve_candidate_input(input_path)
    source = resolved.metadata()
    source["candidate_input_path"] = str(input_path)
    return build_candidate(resolved.candidate_path, repo_root, source)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--expect-failure", action="store_true")
    args = parser.parse_args()
    result = certify_candidate_input(args.candidate, args.repo_root)
    print(json.dumps(result.__dict__, default=str, indent=2, sort_keys=True))
    if args.expect_failure:
        return 0 if result.status != "proof_succeeded" else 1
    return 0 if result.status == "proof_succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
