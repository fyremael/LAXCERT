import LaxCert

namespace LaxCert.Generated.Matrix2x2OffDiagonalZero

def candidateId : String := "Matrix2x2OffDiagonalZero"

def generatedBy : String := "laxforge_laxcert.emitter_contract"

def evolution : ScalarExpr.Evolution := fun field =>
  match field with
  | .u => ScalarExpr.zero
  | .p => ScalarExpr.jetDx .p 1
  | .q => ScalarExpr.zero

def L_0_0 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.ofCoeffs 0 (fun k => ScalarExpr.zero)

def L_0_1 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.ofCoeffs 0 (fun k => ScalarExpr.jetDx .p 0)

def L_1_0 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.ofCoeffs 0 (fun k => ScalarExpr.jetDx .p 0)

def L_1_1 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.ofCoeffs 0 (fun k => ScalarExpr.zero)

def L : MatrixOp 2 ScalarExpr 0 := fun i j =>
  if i.val = 0 then if j.val = 0 then L_0_0 else L_0_1 else if j.val = 0 then L_1_0 else L_1_1

def P_0_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.one)

def P_0_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_1_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_1_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.one)

def P : MatrixOp 2 ScalarExpr 1 := fun i j =>
  if i.val = 0 then if j.val = 0 then P_0_0 else P_0_1 else if j.val = 0 then P_1_0 else P_1_1

def dtOp (A : BoundedDiffOp ScalarExpr 0) : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.Dt evolution (BoundedDiffOp.coeffNat A 0) else ScalarExpr.zero)

def laxResidual_0_0 : BoundedDiffOp ScalarExpr 1 :=
  (dtOp (L (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))) - (((BoundedDiffOp.composeToBound 1 (P (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (L (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (P (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (L (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)))) - ((BoundedDiffOp.composeToBound 1 (L (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (P (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (L (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (P (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)))))

def laxResidual_0_1 : BoundedDiffOp ScalarExpr 1 :=
  (dtOp (L (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))) - (((BoundedDiffOp.composeToBound 1 (P (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (L (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (P (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (L (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)))) - ((BoundedDiffOp.composeToBound 1 (L (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (P (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (L (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (P (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)))))

def laxResidual_1_0 : BoundedDiffOp ScalarExpr 1 :=
  (dtOp (L (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))) - (((BoundedDiffOp.composeToBound 1 (P (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (L (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (P (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (L (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)))) - ((BoundedDiffOp.composeToBound 1 (L (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (P (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (L (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (P (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)))))

def laxResidual_1_1 : BoundedDiffOp ScalarExpr 1 :=
  (dtOp (L (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))) - (((BoundedDiffOp.composeToBound 1 (P (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (L (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (P (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (L (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)))) - ((BoundedDiffOp.composeToBound 1 (L (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) (P (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))) + (BoundedDiffOp.composeToBound 1 (L (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) (P (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)))))

def laxResidual : MatrixOp 2 ScalarExpr 1 := fun i j =>
  if i.val = 0 then if j.val = 0 then laxResidual_0_0 else laxResidual_0_1 else if j.val = 0 then laxResidual_1_0 else laxResidual_1_1

def laxCoefficientAt (i : Fin 2) (j : Fin 2) (k : Fin 2) : Prop :=
  ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero

def laxCoefficientCertificate : Prop :=
  ∀ i j k, ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero

theorem laxCoefficientCertificate_indexed :
    ∀ i j k, ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero := by
  intro i j k
  have h_i : i.val = 0 ∨ i.val = 1 := by omega
  rcases h_i with h_i | h_i <;>
    have h_j : j.val = 0 ∨ j.val = 1 := by omega
  all_goals
    rcases h_j with h_j | h_j <;>
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

def selfAdjointResidualL_0_0 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) - (L (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))

def selfAdjointResidualL_0_1 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) - (L (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))

def selfAdjointResidualL_1_0 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) - (L (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2))

def selfAdjointResidualL_1_1 : BoundedDiffOp ScalarExpr 0 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) - (L (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2))

def selfAdjointResidualL : MatrixOp 2 ScalarExpr 0 := fun i j =>
  if i.val = 0 then if j.val = 0 then selfAdjointResidualL_0_0 else selfAdjointResidualL_0_1 else if j.val = 0 then selfAdjointResidualL_1_0 else selfAdjointResidualL_1_1

def selfAdjointLCoefficientAt (i : Fin 2) (j : Fin 2) (k : Fin 1) : Prop :=
  ScalarExpr.simplify (((selfAdjointResidualL i j).coeff k)) = ScalarExpr.zero

def selfAdjointLCoefficientCertificate : Prop :=
  ∀ i j k, ScalarExpr.simplify (((selfAdjointResidualL i j).coeff k)) = ScalarExpr.zero

theorem selfAdjointLCoefficientCertificate_indexed :
    ∀ i j k, ScalarExpr.simplify (((selfAdjointResidualL i j).coeff k)) = ScalarExpr.zero := by
  intro i j k
  have h_i : i.val = 0 ∨ i.val = 1 := by omega
  rcases h_i with h_i | h_i <;>
    have h_j : j.val = 0 ∨ j.val = 1 := by omega
  all_goals
    rcases h_j with h_j | h_j <;>
      have h_k : k.val = 0 := by omega
  all_goals
    simp only [selfAdjointResidualL, h_i, h_j]
  all_goals
    first
      | have h_k_eq : k = (⟨0, by decide⟩ : Fin 1) := by apply Fin.ext; assumption
    subst k
    native_decide

theorem candidate_self_adjoint_L : selfAdjointLCoefficientCertificate := by
  exact selfAdjointLCoefficientCertificate_indexed

def skewAdjointResidualP_0_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) - (-(P (⟨0, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)))

def skewAdjointResidualP_0_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)) - (-(P (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)))

def skewAdjointResidualP_1_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨0, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) - (-(P (⟨1, by decide⟩ : Fin 2) (⟨0, by decide⟩ : Fin 2)))

def skewAdjointResidualP_1_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)) - (-(P (⟨1, by decide⟩ : Fin 2) (⟨1, by decide⟩ : Fin 2)))

def skewAdjointResidualP : MatrixOp 2 ScalarExpr 1 := fun i j =>
  if i.val = 0 then if j.val = 0 then skewAdjointResidualP_0_0 else skewAdjointResidualP_0_1 else if j.val = 0 then skewAdjointResidualP_1_0 else skewAdjointResidualP_1_1

def skewAdjointPCoefficientAt (i : Fin 2) (j : Fin 2) (k : Fin 2) : Prop :=
  ScalarExpr.simplify (((skewAdjointResidualP i j).coeff k)) = ScalarExpr.zero

def skewAdjointPCoefficientCertificate : Prop :=
  ∀ i j k, ScalarExpr.simplify (((skewAdjointResidualP i j).coeff k)) = ScalarExpr.zero

theorem skewAdjointPCoefficientCertificate_indexed :
    ∀ i j k, ScalarExpr.simplify (((skewAdjointResidualP i j).coeff k)) = ScalarExpr.zero := by
  intro i j k
  have h_i : i.val = 0 ∨ i.val = 1 := by omega
  rcases h_i with h_i | h_i <;>
    have h_j : j.val = 0 ∨ j.val = 1 := by omega
  all_goals
    rcases h_j with h_j | h_j <;>
      have h_k : k.val = 0 ∨ k.val = 1 := by omega
  all_goals
    rcases h_k with h_k | h_k <;>
      simp only [skewAdjointResidualP, h_i, h_j]
  all_goals
    first
      | have h_k_eq : k = (⟨0, by decide⟩ : Fin 2) := by apply Fin.ext; assumption
      | have h_k_eq : k = (⟨1, by decide⟩ : Fin 2) := by apply Fin.ext; assumption
    subst k
    native_decide

theorem candidate_skew_adjoint_P : skewAdjointPCoefficientCertificate := by
  exact skewAdjointPCoefficientCertificate_indexed

end LaxCert.Generated.Matrix2x2OffDiagonalZero
