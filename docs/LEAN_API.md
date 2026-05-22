# Lean API Specification

## 1. Namespace

All formal definitions live under:

```lean
namespace LaxCert
```

Generated candidates live under:

```lean
namespace LaxCert.Generated.<CandidateName>
```

## 2. Module contracts

### `LaxCert.Algebra.ScalarExpr`

Purpose: scalar differential-polynomial expressions.

Required concepts:

- rational constants;
- field jet variables;
- addition, multiplication, negation, powers;
- decidable equality for generated ASTs;
- evaluation into a target commutative semiring/ring when needed.

### `LaxCert.Algebra.Jet`

Purpose: encode fields and derivative order.

Core shape:

```lean
inductive FieldName
  | u
  | p
  | q

def JetVar := FieldName × Nat
```

`(FieldName.u, 0)` means `u`; `(FieldName.u, 2)` means `u_xx`.

### `LaxCert.Algebra.Derivation`

Purpose: formal derivations and laws.

```lean
class IsDerivation (R : Type u) [CommSemiring R] (D : R → R) : Prop where
  map_add : ∀ a b, D (a + b) = D a + D b
  map_mul : ∀ a b, D (a * b) = D a * b + a * D b
```

The implementation may require stronger algebraic assumptions for subtraction and commutators.

### `LaxCert.Operator.DiffOp`

Purpose: formal finite-order differential operators.

MVP representation:

```lean
structure BoundedDiffOp (R : Type u) (N : Nat) where
  coeff : Fin (N+1) → R
```

Interpretation:

\[
A = \sum_{k=0}^N a_k D_x^k.
\]

### `LaxCert.Operator.Compose`

Purpose: implement operator composition in normal form.

Mathematical rule:

\[
(aD^m) \circ (bD^n)
= \sum_{j=0}^{m} \binom{m}{j} a(D^j b)D^{m-j+n}.
\]

Required theorem:

```lean
theorem compose_coeff_correct : ...
```

The exact statement may be representation-dependent, but the exported theorem must say that computed composition coefficients match the Leibniz formula.

### `LaxCert.Operator.Adjoint`

Purpose: formal adjoints.

Required declarations:

```lean
def formalAdjoint : BoundedDiffOp R N → BoundedDiffOp R N' := ...
def SelfAdjoint (A : BoundedDiffOp R N) : Prop := formalAdjoint A = A
def SkewAdjoint (A : BoundedDiffOp R N) : Prop := formalAdjoint A = -A
```

For matrices:

```lean
def matrixFormalAdjoint (A : Matrix (Fin n) (Fin n) (BoundedDiffOp R N)) := ...
```

### `LaxCert.Matrix.Commutator`

Purpose: matrix commutators over differential operators.

Required declarations:

```lean
def matCompose : MatrixOp n R M → MatrixOp n R N → MatrixOp n R K := ...
def matCommutator A B := matCompose A B - matCompose B A
```

Required theorem:

```lean
theorem mat_commutator_entry :
  (matCommutator A B) i j =
    Finset.sum Finset.univ (fun k => compose (A i k) (B k j)) -
    Finset.sum Finset.univ (fun k => compose (B i k) (A k j)) := ...
```

### `LaxCert.ZeroCurvature.LaxEquation`

Purpose: Lax equation certificates.

```lean
def LaxResidual (Dt : R → R) (L P : MatrixOp n R N) : MatrixOp n R K :=
  mapMatrixOp Dt L - matCommutator P L

def SatisfiesLaxEquation (Dt : R → R) (L P : MatrixOp n R N) : Prop :=
  LaxResidual Dt L P = 0
```

Generated theorem form:

```lean
theorem candidate_satisfies_lax_equation :
  SatisfiesLaxEquation Dt L P := by
  -- generated proof
```

### `LaxCert.ZeroCurvature.Basic`

Purpose: connection-form zero curvature.

```lean
def scalarMatrixCommutator (A B : Matrix (Fin n) (Fin n) R) := A * B - B * A

def ZeroCurvature (Dx Dt : R → R) (U V : Matrix (Fin n) (Fin n) R) : Prop :=
  mapMatrix Dt U - mapMatrix Dx V + scalarMatrixCommutator U V = 0
```

### `LaxCert.ZeroCurvature.Gauge`

Post-MVP purpose: gauge transformations and invariance.

Required theorem:

```lean
theorem gauge_preserves_zero_curvature :
  ZeroCurvature Dx Dt U V →
  ZeroCurvature Dx Dt (gaugeU Dx G U) (gaugeV Dt G V) := ...
```

The full statement will require invertibility of `G`, compatible derivation laws, and matrix inverse identities.
