import LaxCert

namespace LaxCert.Generated.ToyLaxZero

def candidateId : String := "ToyLaxZero"

def generatedBy : String := "laxforge_laxcert.emitter_contract"

def evolution : ScalarExpr.Evolution := fun field =>
  match field with
  | .u => ScalarExpr.zero
  | .p => ScalarExpr.jetDx .p 1
  | .q => ScalarExpr.zero

def L_0_0 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.ofCoeffs 0 (fun k => ScalarExpr.jetDx .p 0)

def L : MatrixOp 1 ScalarExpr 0 := fun i j =>
  L_0_0

def P_0_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.one)

def P : MatrixOp 1 ScalarExpr 1 := fun i j =>
  P_0_0

def dtOp (A : BoundedDiffOp ScalarExpr 0) : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.Dt evolution (BoundedDiffOp.coeffNat A 0) else ScalarExpr.zero)

def laxResidual_0_0 : BoundedDiffOp ScalarExpr 1 :=
  (dtOp (L (⟨0, by decide⟩ : Fin 1) (⟨0, by decide⟩ : Fin 1))) - ((BoundedDiffOp.composeToBound 1 (P (⟨0, by decide⟩ : Fin 1) (⟨0, by decide⟩ : Fin 1)) (L (⟨0, by decide⟩ : Fin 1) (⟨0, by decide⟩ : Fin 1))) - (BoundedDiffOp.composeToBound 1 (L (⟨0, by decide⟩ : Fin 1) (⟨0, by decide⟩ : Fin 1)) (P (⟨0, by decide⟩ : Fin 1) (⟨0, by decide⟩ : Fin 1))))

def laxResidual : MatrixOp 1 ScalarExpr 1 := fun i j =>
  laxResidual_0_0

def laxCoefficientAt (i : Fin 1) (j : Fin 1) (k : Fin 2) : Prop :=
  ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero

def laxCoefficientCertificate : Prop :=
  ∀ i j k, ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero

theorem laxCoefficientCertificate_indexed :
    ∀ i j k, ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero := by
  intro i j k
  have h_i : i.val = 0 := by omega
  have h_j : j.val = 0 := by omega
  have h_k : k.val = 0 ∨ k.val = 1 := by omega
  all_goals
    rcases h_k with h_k | h_k <;>
      simp only [laxResidual, h_i, h_j]
  all_goals
    first
      | have h_k_eq : k = (⟨0, by decide⟩ : Fin 2) := by apply Fin.ext; assumption
      | have h_k_eq : k = (⟨1, by decide⟩ : Fin 2) := by apply Fin.ext; assumption
    subst k
    native_decide

theorem candidate_satisfies_lax_equation : laxCoefficientCertificate := by
  exact laxCoefficientCertificate_indexed

end LaxCert.Generated.ToyLaxZero
