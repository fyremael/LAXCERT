import LaxCert.Algebra.Jet

namespace LaxCert

/-- Differential-polynomial scalar expressions for phase 1 certificates.

The AST is intentionally small: enough for generated certificates to encode
field jets, rational constants, sums, products, negation, and powers. -/
inductive ScalarExpr where
  | const : Rat -> ScalarExpr
  | jet : JetVar -> ScalarExpr
  | add : ScalarExpr -> ScalarExpr -> ScalarExpr
  | mul : ScalarExpr -> ScalarExpr -> ScalarExpr
  | neg : ScalarExpr -> ScalarExpr
  | pow : ScalarExpr -> Nat -> ScalarExpr
  deriving DecidableEq, Repr

namespace ScalarExpr

def zero : ScalarExpr := .const 0
def one : ScalarExpr := .const 1

instance : Zero ScalarExpr where
  zero := zero

instance : One ScalarExpr where
  one := one

instance : Add ScalarExpr where
  add := .add

instance : Mul ScalarExpr where
  mul := .mul

instance : Neg ScalarExpr where
  neg := .neg

instance : Sub ScalarExpr where
  sub a b := .add a (.neg b)

def u : ScalarExpr := .jet (FieldName.baseJet .u)
def p : ScalarExpr := .jet (FieldName.baseJet .p)
def q : ScalarExpr := .jet (FieldName.baseJet .q)

def jetDx (field : FieldName) (order : Nat) : ScalarExpr :=
  .jet { field, order }

def isConst (value : Rat) : ScalarExpr -> Bool
  | .const c => c == value
  | _ => false

/-- Smart addition with the neutral element removed. -/
def mkAdd (a b : ScalarExpr) : ScalarExpr :=
  match a, b with
  | .const x, .const y =>
      if x == 0 then
        b
      else if y == 0 then
        a
      else if x == -y then
        zero
      else
        .const (x + y)
  | _, _ =>
      if isConst 0 a then
        b
      else if isConst 0 b then
        a
      else
        .add a b

/-- Smart multiplication with zero and one simplified. -/
def mkMul (a b : ScalarExpr) : ScalarExpr :=
  if isConst 0 a then
    zero
  else if isConst 0 b then
    zero
  else if isConst 1 a then
    b
  else if isConst 1 b then
    a
  else
    .mul a b

def mkNeg (a : ScalarExpr) : ScalarExpr :=
  match a with
  | .const n => .const (-n)
  | .neg x => x
  | x => .neg x

@[simp] theorem mkAdd_zero_left (a : ScalarExpr) : mkAdd zero a = a := by
  cases a <;> simp [mkAdd, isConst, zero]

@[simp] theorem mkAdd_zero_right (a : ScalarExpr) : mkAdd a zero = a := by
  cases a <;> simp [mkAdd, isConst, zero]
  · rename_i c
    by_cases hc : c = 0
    · simp [hc]
    · simp [hc]

@[simp] theorem mkMul_zero_left (a : ScalarExpr) : mkMul zero a = zero := by
  rfl

@[simp] theorem mkMul_zero_right (a : ScalarExpr) : mkMul a zero = zero := by
  cases a <;> simp [mkMul, isConst, zero]

@[simp] theorem mkMul_one_left (a : ScalarExpr) : mkMul one a = a := by
  cases a <;> simp [mkMul, isConst, zero, one]
  · rename_i c
    by_cases hc : c = 0
    · simp [hc]
    · simp [hc]

@[simp] theorem mkMul_one_right (a : ScalarExpr) : mkMul a one = a := by
  cases a <;> simp [mkMul, isConst, zero, one]
  · rename_i c
    by_cases hc0 : c = 0
    · simp [hc0]
    · by_cases hc1 : c = 1
      · simp [hc1]
      · simp [hc0, hc1]

def natConst : Nat -> ScalarExpr
  | 0 => zero
  | n + 1 => mkAdd one (natConst n)

/-- A lightweight simplifier used by generated phase 1 scalar proofs. -/
def simplify : ScalarExpr -> ScalarExpr
  | .const n => .const n
  | .jet v => .jet v
  | .add a b =>
      let sa := simplify a
      let sb := simplify b
      match sa, sb with
      | x, .neg y => if x == y then zero else mkAdd x (.neg y)
      | .neg x, y => if x == y then zero else mkAdd (.neg x) y
      | x, y => mkAdd x y
  | .mul a b => mkMul (simplify a) (simplify b)
  | .neg a => mkNeg (simplify a)
  | .pow a n =>
      match n with
      | 0 => one
      | 1 => simplify a
      | k => .pow (simplify a) k

/-- Spatial derivation on scalar differential polynomials.

Constants go to zero, jets shift by one order, and sums/products use the
usual derivation laws. Powers use `D(a^n) = n * a^(n-1) * D(a)`. -/
def Dx : ScalarExpr -> ScalarExpr
  | .const _ => zero
  | .jet v => .jet (JetVar.dx v)
  | .add a b => mkAdd (Dx a) (Dx b)
  | .mul a b => mkAdd (mkMul (Dx a) b) (mkMul a (Dx b))
  | .neg a => mkNeg (Dx a)
  | .pow a n =>
      match n with
      | 0 => zero
      | k + 1 => mkMul (mkMul (natConst (k + 1)) (.pow a k)) (Dx a)

def iterDx : Nat → ScalarExpr → ScalarExpr
  | 0, expr => expr
  | n + 1, expr => iterDx n (Dx expr)

/-- Interpret an AST in a commutative ring-like target, given values for all jet vars.

The coefficient map is explicit so phase 1 does not assume a particular
embedding of rational constants into the target. -/
def eval {R : Type u} [Zero R] [One R] [Add R] [Mul R] [Neg R] [Pow R Nat]
    (coeff : Rat -> R) (rho : JetVar -> R) : ScalarExpr -> R
  | .const n => coeff n
  | .jet v => rho v
  | .add a b => eval coeff rho a + eval coeff rho b
  | .mul a b => eval coeff rho a * eval coeff rho b
  | .neg a => -eval coeff rho a
  | .pow a n => eval coeff rho a ^ n

theorem Dx_p_mul_q :
    Dx (.mul p q) =
      .add (mkMul (jetDx .p 1) q) (mkMul p (jetDx .q 1)) := by
  rfl

theorem simplify_Dx_p_mul_q :
    simplify (Dx (.mul p q)) =
      .add (mkMul (jetDx .p 1) q) (mkMul p (jetDx .q 1)) := by
  rfl

theorem Dx_u_zero_add :
    simplify (Dx (.add u zero)) = jetDx .u 1 := by
  rfl

end ScalarExpr

end LaxCert
