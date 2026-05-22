import LaxCert.Matrix.Commutator
import LaxCert.Algebra.Evolution

namespace LaxCert

namespace MatrixOp

def mapCoeff {n N : Nat}
    (f : ScalarExpr → ScalarExpr)
    (A : MatrixOp n ScalarExpr N) : MatrixOp n ScalarExpr N :=
  fun i j => { coeff := fun k => f ((A i j).coeff k) }

def LaxResidual {n N : Nat}
    (evolution : ScalarExpr.Evolution)
    (L P : MatrixOp n ScalarExpr N) : MatrixOp n ScalarExpr N :=
  mapCoeff (ScalarExpr.Dt evolution) L - commutator P L

def SatisfiesLaxEquation {n N : Nat}
    (evolution : ScalarExpr.Evolution)
    (L P : MatrixOp n ScalarExpr N) : Prop :=
  LaxResidual evolution L P = 0

def NormalizedZero {n N : Nat} (A : MatrixOp n ScalarExpr N) : Prop :=
  ∀ i j k, ScalarExpr.simplify ((A i j).coeff k) = ScalarExpr.zero

end MatrixOp

end LaxCert
