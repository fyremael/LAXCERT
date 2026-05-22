import LaxCert.Algebra.ScalarExpr

namespace LaxCert.Examples.ToyScalar

open LaxCert.ScalarExpr

/-- Phase 1 exit-criterion example:
`D_x(pq) = p_x q + p q_x` in the scalar expression AST. -/
theorem dx_product_rule_for_pq :
    Dx (.mul p q) =
      .add (mkMul (jetDx .p 1) q) (mkMul p (jetDx .q 1)) := by
  rfl

/-- The same identity through the phase 1 simplification path. -/
theorem simplified_dx_product_rule_for_pq :
    simplify (Dx (.mul p q)) =
      .add (mkMul (jetDx .p 1) q) (mkMul p (jetDx .q 1)) := by
  rfl

end LaxCert.Examples.ToyScalar
