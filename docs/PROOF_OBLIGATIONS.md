# Proof Obligations and Acceptance Tests

## 1. Obligations for hand-written Lean core

### O1: coefficient extensionality

Two bounded differential operators are equal iff their coefficients are equal for every order.

### O2: zero and addition laws

Prove that the bounded representation behaves as an additive commutative group when the coefficient ring does.

### O3: operator composition normal form

Prove the implementation agrees with:

\[
(aD^m) \circ (bD^n)
= \sum_{j=0}^{m} \binom{m}{j} a(D^j b)D^{m-j+n}.
\]

### O4: associativity of composition

Prove:

\[
(A \circ B) \circ C = A \circ (B \circ C).
\]

This may be postponed if the MVP generated certificates only use explicit normalization and do not require associativity as a theorem. But the theorem is needed for a robust algebra library.

### O5: commutator sanity

Prove:

\[
[A,A] = 0.
\]

and, over additive groups:

\[
[A,B] = -[B,A].
\]

### O6: matrix composition entry theorem

Prove that matrix operator composition expands entrywise using finite sums over the inner index.

### O7: Lax residual coefficient theorem

Prove that a generated residual is zero if all its normalized coefficients are zero.

### O8: formal adjoint correctness

Prove the formal adjoint laws:

\[
(A+B)^* = A^* + B^*,
\]

\[
(A \circ B)^* = B^* \circ A^*,
\]

under the formal differential operator semantics.

### O9: generated candidate theorem

For each generated candidate:

```lean
theorem candidate_satisfies_lax_equation :
  SatisfiesLaxEquation Dt L P := by
  ...
```

### O10: failure gate

An intentionally false candidate must fail. The CI job should confirm failure, not ignore it.

## 2. Acceptance tests

### A1: toy scalar operator

Use a tiny operator identity where all coefficients are manually known.

### A2: matrix commutator toy

Use a 2×2 matrix with constant coefficients to test matrix commutator shape.

### A3: differential noncommutativity toy

Certify:

\[
D_x \circ f = fD_x + f_x.
\]

This is the essential noncommutative rule.

### A4: formal adjoint toy

Certify:

\[
(fD_x)^* = -fD_x - f_x.
\]

### A5: paired-field 2×2 calibration

Use the LAXFORGE familiar 2×2 operator:

\[
L=
\begin{pmatrix}
D_x^2 & -q \\
p & -D_x^2
\end{pmatrix}.
\]

Certify the declared evolution equations against the generated `P`.

### A6: false pair

Change one sign or coefficient in `P`; the certificate must fail.

## 3. No-sorry policy

Production modules and generated candidate proofs may not contain `sorry`, `admit`, or new axioms.

Practical CI gate:

```bash
grep -R "sorry\|admit\|axiom" lean/LaxCert && exit 1 || true
lake build
```

This is crude but effective for MVP. Later, add an axiom audit per generated theorem.
