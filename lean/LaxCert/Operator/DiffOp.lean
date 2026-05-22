import LaxCert.Algebra.ScalarExpr
import Std.Tactic

namespace LaxCert

/-- Bounded formal differential operator.
`coeff k` is the coefficient of `D_x^k`.
This bounded representation is chosen for generated MVP certificates. -/
structure BoundedDiffOp (R : Type u) (N : Nat) where
  coeff : Fin (N + 1) → R

namespace BoundedDiffOp

theorem ext {R : Type u} {N : Nat} {A B : BoundedDiffOp R N}
    (h : ∀ k, A.coeff k = B.coeff k) : A = B := by
  cases A
  cases B
  congr
  funext k
  exact h k

instance {R : Type u} {N : Nat} [Zero R] : Zero (BoundedDiffOp R N) where
  zero := { coeff := fun _ => 0 }

instance {R : Type u} {N : Nat} [Add R] : Add (BoundedDiffOp R N) where
  add A B := { coeff := fun k => A.coeff k + B.coeff k }

instance {R : Type u} {N : Nat} [Neg R] : Neg (BoundedDiffOp R N) where
  neg A := { coeff := fun k => -A.coeff k }

instance {R : Type u} {N : Nat} [Sub R] : Sub (BoundedDiffOp R N) where
  sub A B := { coeff := fun k => A.coeff k - B.coeff k }

def coeff0 {R : Type u} {N : Nat} (A : BoundedDiffOp R N) : R :=
  A.coeff ⟨0, Nat.zero_lt_succ N⟩

def coeff1 {R : Type u} (A : BoundedDiffOp R 1) : R :=
  A.coeff ⟨1, by omega⟩

def coeffNat {N : Nat} (A : BoundedDiffOp ScalarExpr N) (k : Nat) : ScalarExpr :=
  if h : k < N + 1 then
    A.coeff ⟨k, h⟩
  else
    ScalarExpr.zero

def ofCoeffs (N : Nat) (f : Nat → ScalarExpr) : BoundedDiffOp ScalarExpr N :=
  { coeff := fun k => f k.val }

def sumUpTo : Nat → (Nat → ScalarExpr) → ScalarExpr
  | 0, f => f 0
  | n + 1, f => ScalarExpr.mkAdd (sumUpTo n f) (f (n + 1))

def binom : Nat → Nat → Nat
  | _, 0 => 1
  | 0, _ + 1 => 0
  | n + 1, k + 1 => binom n k + binom n (k + 1)

def composeCoeff
    (M N : Nat)
    (A : BoundedDiffOp ScalarExpr M)
    (B : BoundedDiffOp ScalarExpr N)
    (r : Nat) : ScalarExpr :=
  sumUpTo M fun m =>
    sumUpTo N fun n =>
      sumUpTo m fun j =>
        if r = m - j + n then
          ScalarExpr.mkMul
            (ScalarExpr.mkMul (ScalarExpr.natConst (binom m j)) (coeffNat A m))
            (ScalarExpr.iterDx j (coeffNat B n))
        else
          ScalarExpr.zero

def composeToBound
    (K : Nat)
    {M N : Nat}
    (A : BoundedDiffOp ScalarExpr M)
    (B : BoundedDiffOp ScalarExpr N) : BoundedDiffOp ScalarExpr K :=
  ofCoeffs K (composeCoeff M N A B)

def composeBounded
    {M N : Nat}
    (A : BoundedDiffOp ScalarExpr M)
    (B : BoundedDiffOp ScalarExpr N) : BoundedDiffOp ScalarExpr (M + N) :=
  composeToBound (M + N) A B

def order1 (a0 a1 : ScalarExpr) : BoundedDiffOp ScalarExpr 1 :=
  { coeff := fun k => if k.val = 0 then a0 else a1 }

def order2 (a0 a1 a2 : ScalarExpr) : BoundedDiffOp ScalarExpr 2 :=
  { coeff := fun k =>
      if k.val = 0 then
        a0
      else if k.val = 1 then
        a1
      else
        a2 }

/-- Multiplication by a scalar expression as a zeroth-order operator. -/
def mulBy (f : ScalarExpr) : BoundedDiffOp ScalarExpr 1 :=
  order1 f ScalarExpr.zero

/-- The first spatial differential operator `D_x`. -/
def DxOp : BoundedDiffOp ScalarExpr 1 :=
  order1 ScalarExpr.zero ScalarExpr.one

/-- First-order composition into a second-order normal form.

For `(a0 + a1 D) ∘ (b0 + b1 D)`, the coefficients are:

* order 0: `a0*b0 + a1*Dx(b0)`;
* order 1: `a0*b1 + a1*b0 + a1*Dx(b1)`;
* order 2: `a1*b1`.

This is the phase 2 Leibniz/Ore rule specialized to first-order inputs. -/
def composeFirstOrder
    (A B : BoundedDiffOp ScalarExpr 1) : BoundedDiffOp ScalarExpr 2 :=
  order2
    (ScalarExpr.mkAdd
      (ScalarExpr.mkMul (coeff0 A) (coeff0 B))
      (ScalarExpr.mkMul (coeff1 A) (ScalarExpr.Dx (coeff0 B))))
    (ScalarExpr.mkAdd
      (ScalarExpr.mkAdd
        (ScalarExpr.mkMul (coeff0 A) (coeff1 B))
        (ScalarExpr.mkMul (coeff1 A) (coeff0 B)))
      (ScalarExpr.mkMul (coeff1 A) (ScalarExpr.Dx (coeff1 B))))
    (ScalarExpr.mkMul (coeff1 A) (coeff1 B))

def leibnizDxMulByNormalForm
    (f : ScalarExpr) : BoundedDiffOp ScalarExpr 2 :=
  order2 (ScalarExpr.Dx f) f ScalarExpr.zero

theorem compose_Dx_mulBy_p :
    composeFirstOrder DxOp (mulBy ScalarExpr.p) =
      order2 (ScalarExpr.jetDx .p 1) ScalarExpr.p ScalarExpr.zero := by
  apply ext
  intro k
  have hk : k.val = 0 ∨ k.val = 1 ∨ k.val = 2 := by
    omega
  rcases hk with hk | hk | hk
  · have hfin : k = 0 := by
      apply Fin.ext
      exact hk
    subst k
    rfl
  · have hfin : k = 1 := by
      apply Fin.ext
      exact hk
    subst k
    rfl
  · have hfin : k = 2 := by
      apply Fin.ext
      exact hk
    subst k
    rfl

theorem wrong_sign_rejected_for_p :
    composeFirstOrder DxOp (mulBy ScalarExpr.p) ≠
      order2 (ScalarExpr.mkNeg (ScalarExpr.jetDx .p 1)) ScalarExpr.p ScalarExpr.zero := by
  intro h
  have h0 := congrArg (fun A : BoundedDiffOp ScalarExpr 2 => A.coeff 0) h
  simp [composeFirstOrder, DxOp, mulBy, order1, order2, coeff0, coeff1,
    ScalarExpr.p, ScalarExpr.jetDx, ScalarExpr.Dx, ScalarExpr.mkAdd,
    ScalarExpr.mkMul, ScalarExpr.mkNeg, ScalarExpr.isConst,
    ScalarExpr.zero, ScalarExpr.one] at h0

end BoundedDiffOp

end LaxCert
