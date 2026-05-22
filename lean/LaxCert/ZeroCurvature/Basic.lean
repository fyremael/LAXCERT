namespace LaxCert

def ScalarMatrix (n : Nat) (R : Type u) :=
  Fin n → Fin n → R

namespace ScalarMatrix

instance {n : Nat} [Zero R] : Zero (ScalarMatrix n R) where
  zero := fun _ _ => 0

instance {n : Nat} [Add R] : Add (ScalarMatrix n R) where
  add A B := fun i j => A i j + B i j

instance {n : Nat} [Sub R] : Sub (ScalarMatrix n R) where
  sub A B := fun i j => A i j - B i j

def map {n : Nat} (f : R → S) (A : ScalarMatrix n R) : ScalarMatrix n S :=
  fun i j => f (A i j)

def commutator {n : Nat} [Sub R] (A B : ScalarMatrix n R) : ScalarMatrix n R :=
  A - B

def ZeroCurvature {n : Nat} [Zero R] [Add R] [Sub R]
    (Dx Dt : R → R) (U V : ScalarMatrix n R) : Prop :=
  map Dt U - map Dx V + commutator U V = 0

end ScalarMatrix

end LaxCert
