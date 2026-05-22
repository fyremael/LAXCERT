import LaxCert.Algebra.ScalarExpr

namespace LaxCert

namespace ScalarExpr

/-- A phase-MVP evolution assigns a time derivative to each base field. -/
def Evolution := FieldName → ScalarExpr

/-- Temporal derivation induced by declared base-field evolution. -/
def Dt (evolution : Evolution) : ScalarExpr → ScalarExpr
  | .const _ => zero
  | .jet v => ScalarExpr.iterDx v.order (evolution v.field)
  | .add a b => mkAdd (Dt evolution a) (Dt evolution b)
  | .mul a b => mkAdd (mkMul (Dt evolution a) b) (mkMul a (Dt evolution b))
  | .neg a => mkNeg (Dt evolution a)
  | .pow a n =>
      match n with
      | 0 => zero
      | k + 1 => mkMul (mkMul (natConst (k + 1)) (.pow a k)) (Dt evolution a)

end ScalarExpr

end LaxCert
