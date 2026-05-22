namespace LaxCert

universe u

/-- A lightweight derivation law contract for the LAXCERT MVP.
The final implementation should align this with mathlib conventions where practical. -/
class IsDerivation (R : Type u) [Add R] [Mul R] (D : R → R) : Prop where
  map_add : ∀ a b : R, D (a + b) = D a + D b
  map_mul : ∀ a b : R, D (a * b) = D a * b + a * D b

end LaxCert
