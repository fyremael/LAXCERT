import LaxCert.Operator.DiffOp

namespace LaxCert

namespace BoundedDiffOp

/-- MVP formal adjoint placeholder over fixed bounds.

Generated candidates are checked by the Python normalizer for now; this Lean
surface gives stable predicates for generated theorem names and future proofs. -/
def formalAdjoint {N : Nat} (A : BoundedDiffOp ScalarExpr N) : BoundedDiffOp ScalarExpr N :=
  A

def SelfAdjoint {N : Nat} (A : BoundedDiffOp ScalarExpr N) : Prop :=
  formalAdjoint A = A

def SkewAdjoint {N : Nat} [Neg ScalarExpr] (A : BoundedDiffOp ScalarExpr N) : Prop :=
  formalAdjoint A = -A

theorem selfAdjoint_refl {N : Nat} (A : BoundedDiffOp ScalarExpr N) :
    SelfAdjoint A := by
  rfl

/-- Formal adjoint for first-order scalar operators.

For `a0 + a1 D`, this is `(a0 - Dx a1) - a1 D`. -/
def formalAdjointFirstOrder (A : BoundedDiffOp ScalarExpr 1) :
    BoundedDiffOp ScalarExpr 1 :=
  order1
    (ScalarExpr.mkAdd (coeff0 A) (ScalarExpr.mkNeg (ScalarExpr.Dx (coeff1 A))))
    (ScalarExpr.mkNeg (coeff1 A))

def adjointCoeff {N : Nat} (A : BoundedDiffOp ScalarExpr N) (r : Nat) :
    ScalarExpr :=
  sumUpTo N fun k =>
    if r ≤ k then
      let j := k - r
      let factor :=
        if k % 2 = 0 then
          ScalarExpr.natConst (binom k j)
        else
          ScalarExpr.mkNeg (ScalarExpr.natConst (binom k j))
      ScalarExpr.mkMul factor (ScalarExpr.iterDx j (coeffNat A k))
    else
      ScalarExpr.zero

def formalAdjointBounded {N : Nat} (A : BoundedDiffOp ScalarExpr N) :
    BoundedDiffOp ScalarExpr N :=
  ofCoeffs N (adjointCoeff A)

end BoundedDiffOp

end LaxCert
