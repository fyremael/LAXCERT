# SPEC: LAXCERT — A Lean4 Companion for LAXFORGE

## 0. Executive summary

LAXCERT is a Lean4 proof companion for LAXFORGE. It does not search the space of Lax pairs. It does not replace symbolic computation. It accepts a structured certificate emitted by LAXFORGE and verifies, in a small trusted kernel, that the declared algebraic claim holds under explicit assumptions.

The first production target is not a full formalization of integrable systems. The first target is narrower and more useful:

1. Represent scalar differential-polynomial expressions over fields such as `u`, `p`, and `q` and their `x`-derivatives.
2. Represent formal scalar differential operators as finite sums `Σ a_k D_x^k`.
3. Represent matrix differential operators entrywise.
4. Normalize operator products using the Leibniz/Ore rule.
5. Verify Lax equations of the form `L_t = [P,L]`.
6. Verify zero-curvature equations of the form `U_t - V_x + [U,V] = 0`.
7. Verify declared adjointness properties: `SelfAdjoint L`, `SkewAdjoint P`.
8. Later, verify gauge equivalence and gauge invariance.

The companion converts LAXFORGE claims into proof-carrying mathematical artifacts. A candidate is not merely simplified to zero by SymPy. It is checked by Lean against a declared algebra, declared derivations, declared field evolutions, and declared normal-form semantics.

## 1. Scope

### 1.1 In scope for MVP

The MVP covers one-dimensional formal differential operator Lax pairs.

The canonical MVP form is:

\[
L = \sum_{k=0}^{m} A_k D_x^k,
\qquad
P = \sum_{k=0}^{n} B_k D_x^k,
\]

where each `A_k` and `B_k` may be a scalar expression or a matrix of scalar expressions, and where scalar expressions are differential polynomials in finitely many fields.

The MVP explicitly supports:

- spatial direction: `x`;
- time direction: `t` only as an evolution derivation on fields;
- fields: `u`, or paired fields `p,q`;
- derivatives: `u_x`, `u_xx`, `p_x`, `q_x`, etc.;
- formal powers: `D(x)^k` represented by natural-number order `k`;
- operator composition using the generalized Leibniz rule;
- commutators `[P,L] = P ∘ L - L ∘ P`;
- generated certificates for `L_t = [P,L]`;
- generated certificates for `SelfAdjoint L` and `SkewAdjoint P` when declared;
- intentionally false candidates that must fail CI.

### 1.2 Out of scope for MVP

The MVP does not attempt:

- full PDE theory;
- inverse scattering;
- analytic function spaces;
- domains of unbounded operators;
- Hilbert-space spectral theory;
- multi-dimensional differential geometry;
- proof search over unknown ansatz coefficients;
- automatic discovery of new Lax pairs inside Lean;
- a complete library of known integrable systems.

The guiding rule is: **formalize the algebraic certificate first, not the entire mathematical universe around it.**

## 2. Design doctrine

### 2.1 Separation of concerns

LAXFORGE owns:

- ansatz generation;
- symbolic solving;
- coefficient matching;
- gauge reduction heuristics;
- cyclic-basis computation;
- prior-art comparison;
- simplification;
- candidate ranking;
- proof-certificate emission.

LAXCERT owns:

- formal definitions;
- normalization semantics;
- theorem statements;
- proof checking;
- failure reporting;
- proof-status artifacts.

AETHER owns:

- provenance ledger;
- artifact hashes;
- candidate lineage;
- proof status;
- rejection status;
- policy and visibility.

MODULUS owns:

- geometric interpretation;
- operator/dynamics interpretation;
- architectural relevance to learning systems.

### 2.2 Trust boundary

LAXFORGE may be clever. LAXCERT must be small, boring, and hard to fool.

The trusted boundary consists of:

1. Lean kernel.
2. LAXCERT definitions.
3. Generated Lean source from certificate ASTs.
4. CI command that checks the generated Lean files.

SymPy simplification is not trusted as proof. It is trusted only as a guide for proof generation.

### 2.3 Artifact principle

Every candidate should have a complete evidence folder:

```text
candidate_id/
  candidate.json
  candidate.normalized.json
  generated.lean
  generated.hash
  lake-build.log
  proof-status.json
  assumptions.json
  provenance.json
```

The artifact should be reconstructible. A future reviewer should be able to rebuild the proof from the JSON certificate and the pinned Lean/LAXCERT version.

## 3. Core mathematical objects

### 3.1 Scalar expression algebra

The MVP scalar algebra is a differential-polynomial algebra over rational coefficients:

\[
\mathbb{Q}[u_0,u_1,u_2,\ldots]
\]

where `u_k` denotes `D_x^k u`. For paired fields:

\[
\mathbb{Q}[p_0,p_1,p_2,\ldots,q_0,q_1,q_2,\ldots].
\]

For finite generated certificates, the actual algebra is bounded by the maximum derivative order appearing in the certificate after normalization.

### 3.2 Spatial derivation

The spatial derivation `Dx` is defined on jet variables by:

\[
D_x(u_k) = u_{k+1}.
\]

and extended by linearity and the product rule.

### 3.3 Temporal derivation

The temporal derivation `Dt` is defined by the declared evolution equation. If

\[
u_t = F(u,u_x,u_{xx},\ldots),
\]

then

\[
D_t(u_k) = D_x^k F.
\]

For paired fields:

\[
p_t = F_p(p,q,p_x,q_x,\ldots),
\qquad
q_t = F_q(p,q,p_x,q_x,\ldots).
\]

The certificate must declare the evolution equations used to interpret `L_t` or `U_t`.

### 3.4 Formal differential operators

A scalar differential operator is a finite formal sum:

\[
A = \sum_{k=0}^{N} a_k D_x^k.
\]

Composition is determined by the generalized Leibniz rule:

\[
D_x^m \circ a
= \sum_{j=0}^{m} {m \choose j} (D_x^j a) D_x^{m-j}.
\]

Therefore:

\[
(a D_x^m) \circ (b D_x^n)
= \sum_{j=0}^{m} {m \choose j} a (D_x^j b) D_x^{m-j+n}.
\]

This formula is the normal-form engine for the MVP.

### 3.5 Matrix differential operators

A matrix differential operator is a matrix whose entries are scalar differential operators. Composition is matrix multiplication where entry multiplication is operator composition:

\[
(A \circ B)_{ij} = \sum_k A_{ik} \circ B_{kj}.
\]

The commutator is:

\[
[A,B] = A \circ B - B \circ A.
\]

### 3.6 Adjoint

For scalar operators, define formal adjoint by:

\[
(a D_x^k)^* = (-D_x)^k \circ a.
\]

For matrix operators:

\[
(A^*)_{ij} = (A_{ji})^*.
\]

Then:

- `SelfAdjoint L` means `L^* = L`.
- `SkewAdjoint P` means `P^* = -P`.

The MVP only uses formal adjoints, not Hilbert-space domain theory.

## 4. Lean module design

The Lean project is called `LaxCert`.

Proposed module tree:

```text
LaxCert/
  Algebra/
    ScalarExpr.lean
    Jet.lean
    Derivation.lean
    Evolution.lean
  Operator/
    DiffOp.lean
    Compose.lean
    NormalForm.lean
    Adjoint.lean
  Matrix/
    MatrixDiffOp.lean
    Commutator.lean
  ZeroCurvature/
    Basic.lean
    LaxEquation.lean
    Gauge.lean
  Generated/
    Candidate*.lean
  Examples/
    ToyScalar.lean
    AKNSLike2x2.lean
```

### 4.1 Implementation choice: bounded normal forms first

For the generated-proof MVP, use bounded normal forms. Instead of beginning with a sophisticated finitely-supported map library, emit each candidate with a known maximum order:

```lean
structure BoundedDiffOp (R : Type u) (N : Nat) where
  coeff : Fin (N+1) → R
```

This is not maximally elegant, but it is easy to generate, easy to normalize, and easy to inspect.

A later version may replace this with `Finsupp Nat R` or a dedicated sparse representation.

### 4.2 Proof strategy

The compiler path is:

```text
candidate AST
  → normalized operator coefficients
  → generated Lean definitions
  → generated theorem statement
  → normalization lemma application
  → coefficient-wise scalar equality
  → ring/ring_nf/simp-style discharge
```

The Lean side should not rely on fragile expression-level coincidences. It should reduce claims to coefficient equalities.

## 5. Candidate schema

A LAXCERT candidate certificate contains:

- `candidate_id`;
- `laxforge_version`;
- `laxcert_schema_version`;
- `fields`;
- `directions`;
- `scalar_ring`;
- `evolution`;
- `L`;
- `P`;
- optional `U,V` for zero-curvature matrix connection form;
- claims;
- assumptions;
- proof strategy;
- source provenance;
- prior-art metadata;
- gauge-reduction metadata.

The schema is intentionally AST-based. Strings are allowed only for human-readable display, not as the authoritative certificate representation.

## 6. Python emitter contract

The Python-side emitter must:

1. Validate the candidate against `laxcert_candidate.schema.json`.
2. Canonicalize scalar expressions.
3. Expand differential operator compositions into bounded normal form.
4. Compute maximum differential order after normalization.
5. Emit Lean definitions with explicit bounds.
6. Emit proof skeletons.
7. Run `lake build` against the generated file.
8. Emit `proof-status.json`.

The emitter must not silently discard assumptions. Every assumption used by LAXFORGE must appear in the candidate JSON and in the Lean theorem context.

## 7. Theorem surface

The first formal theorem surface should include:

```lean
namespace LaxCert

-- scalar differential-polynomial expression layer
class HasDx (R : Type u) where
  Dx : R → R

class HasDt (R : Type u) where
  Dt : R → R

-- derivation laws
class IsDerivation (R : Type u) [CommSemiring R] (D : R → R) : Prop where
  map_add : ∀ a b, D (a + b) = D a + D b
  map_mul : ∀ a b, D (a * b) = D a * b + a * D b

-- bounded operator normal form
structure BoundedDiffOp (R : Type u) (N : Nat) where
  coeff : Fin (N+1) → R

-- composition and commutator
def compose : BoundedDiffOp R M → BoundedDiffOp R N → BoundedDiffOp R K := ...
def commutator (A B : BoundedDiffOp R N) := compose A B - compose B A

-- matrix lift
def MatrixDiffOp (n : Nat) (R : Type u) (N : Nat) := Matrix (Fin n) (Fin n) (BoundedDiffOp R N)

-- main claims
def LaxEquation (Dt : R → R) (L P Lt : MatrixDiffOp n R N) : Prop :=
  Lt = commutator P L

def ZeroCurvature (Dx Dt : R → R) (U V : Matrix n n R) : Prop :=
  mapMatrix Dt U - mapMatrix Dx V + commutatorMatrix U V = 0

end LaxCert
```

The real implementation will refine dependent bounds and casts. The spec-level API names should remain stable even if internal representations change.

## 8. Proof obligations

### P0: sanity proofs

- addition and zero laws for bounded operators;
- coefficient extensionality;
- commutator with self is zero;
- commutator antisymmetry where subtraction is available;
- matrix commutator entry formula.

### P1: derivation lift proofs

- derivation acts entrywise on matrices;
- derivation respects matrix addition;
- derivation respects matrix multiplication when scalar multiplication obeys Leibniz;
- `Dt(Dx^k field) = Dx^k(Dt field)` under declared commuting derivations, where applicable.

### P2: differential-operator normal form proofs

- correctness of composition formula;
- associativity of operator composition;
- correctness of commutator expansion;
- coefficient-wise equality implies operator equality.

### P3: Lax equation proof

For each generated candidate:

\[
L_t - [P,L] = 0.
\]

Proof reduces to all operator coefficients being zero.

### P4: adjoint proof

For each generated candidate declaring adjointness:

\[
L^* = L,
\qquad
P^* = -P.
\]

### P5: gauge proof

After MVP:

- define gauge transform;
- prove curvature invariance;
- certify that two candidates are gauge-equivalent under a declared `G`.

## 9. CI gates

LAXCERT CI must include:

1. `lake build` for hand-written modules.
2. `lake build` for generated examples.
3. no `sorry` in production modules.
4. no undeclared axioms in production theorem outputs.
5. positive toy candidate passes.
6. positive AKNS-like 2×2 candidate passes.
7. intentionally false candidate fails.
8. schema validation for candidate JSON.
9. deterministic regeneration check: JSON → Lean file has stable hash.

The false-candidate gate is non-negotiable. A certifier that only reports successes is not a certifier.

## 10. Example first target

The first serious calibration target should be the paired-field 2×2 operator form already familiar to the LAXFORGE thread:

\[
L=
\begin{pmatrix}
D_x^2 & -q \\
p & -D_x^2
\end{pmatrix}.
\]

Use the known candidate `P` and declared evolution equations as a calibration case. The Lean proof should certify that the commutator collapses to the declared `L_t`, with all higher-order differential operator terms cancelling.

This target is good because it tests:

- matrix operator composition;
- noncommutativity of `D_x` and multiplication by fields;
- off-diagonal evolution;
- cancellation of higher-order differential terms;
- adjoint/skew-adjoint structure.

## 11. Failure modes

LAXCERT must distinguish:

- schema invalid;
- unsupported expression form;
- unbound field;
- undeclared derivative direction;
- proof failed after normalization;
- Lean type error;
- nonzero residual found;
- unsupported assumption;
- generated code failed deterministic hash check;
- candidate proved but only under assumptions too strong for the mathematical claim.

This matters because failed proof is useful information. It tells LAXFORGE whether the candidate is false, ill-typed, unsupported, or merely beyond the current prover fragment.

## 12. Naming

Recommended names:

- project: `LAXCERT`;
- Lean namespace: `LaxCert`;
- Python package: `laxforge_laxcert`;
- artifact schema: `laxcert_candidate.schema.json`;
- AETHER capability name: `laxcert.verify_candidate`.

## 13. Definition of done for MVP

MVP is done when:

1. A candidate JSON can be emitted from LAXFORGE.
2. The JSON validates against the schema.
3. Lean files are generated deterministically.
4. Hand-written Lean modules compile.
5. At least one toy Lax equation compiles.
6. At least one nontrivial 2×2 differential-operator candidate compiles.
7. At least one intentionally false candidate fails.
8. Proof status is recorded in an AETHER-compatible ledger object.
9. The entire process runs in CI from a clean checkout.

## 14. Strategic value

LAXCERT gives LAXFORGE epistemic finality.

Without LAXCERT, LAXFORGE says:

> This candidate appears to simplify correctly.

With LAXCERT, LAXFORGE says:

> This candidate satisfies the declared Lax equation in the declared formal operator algebra, under declared assumptions, as checked by Lean.

That is the difference between plausible symbolic output and a mathematical artifact.
