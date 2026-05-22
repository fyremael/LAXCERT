import LaxCert.Operator.DiffOp

namespace LaxCert

/-- Matrix differential operators as finite functions over `Fin n`.

This keeps the MVP core dependency-light while exposing the same entrywise API
that generated candidates use. -/
def MatrixOp (n : Nat) (R : Type u) (N : Nat) :=
  Fin n → Fin n → BoundedDiffOp R N

namespace MatrixOp

def zero {n N : Nat} [Zero R] : MatrixOp n R N :=
  fun _ _ => 0

instance {n N : Nat} [Zero R] : Zero (MatrixOp n R N) where
  zero := zero

instance {n N : Nat} [Add R] : Add (MatrixOp n R N) where
  add A B := fun i j => A i j + B i j

instance {n N : Nat} [Sub R] : Sub (MatrixOp n R N) where
  sub A B := fun i j => A i j - B i j

instance {n N : Nat} [Neg R] : Neg (MatrixOp n R N) where
  neg A := fun i j => -(A i j)

/-- MVP entrywise commutator surface.

The Python certifier performs the full Ore-normalized matrix composition for
generated candidates. This Lean API remains stable for generated theorem names
and future in-kernel normalization proofs. -/
def commutator {n N : Nat} [Sub R] (A B : MatrixOp n R N) : MatrixOp n R N :=
  A - B

theorem commutator_entry {n N : Nat} [Sub R]
    (A B : MatrixOp n R N) (i j : Fin n) :
    commutator A B i j = A i j - B i j := by
  rfl

end MatrixOp

end LaxCert
