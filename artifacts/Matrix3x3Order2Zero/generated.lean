import LaxCert

namespace LaxCert.Generated.Matrix3x3Order2Zero

def candidateId : String := "Matrix3x3Order2Zero"

def generatedBy : String := "laxforge_laxcert.emitter_contract"

def evolution : ScalarExpr.Evolution := fun field =>
  match field with
  | .u => ScalarExpr.zero
  | .p => ScalarExpr.zero
  | .q => ScalarExpr.zero

def L_0_0 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.one)

def L_0_1 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.zero)

def L_0_2 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.zero)

def L_1_0 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.zero)

def L_1_1 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.one)

def L_1_2 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.zero)

def L_2_0 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.zero)

def L_2_1 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.zero)

def L_2_2 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.ofCoeffs 2 (fun k => if k = 0 then ScalarExpr.zero else if k = 1 then ScalarExpr.zero else ScalarExpr.one)

def L : MatrixOp 3 ScalarExpr 2 := fun i j =>
  if i.val = 0 then if j.val = 0 then L_0_0 else if j.val = 1 then L_0_1 else L_0_2 else if i.val = 1 then if j.val = 0 then L_1_0 else if j.val = 1 then L_1_1 else L_1_2 else if j.val = 0 then L_2_0 else if j.val = 1 then L_2_1 else L_2_2

def P_0_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.one)

def P_0_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_0_2 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_1_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_1_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.one)

def P_1_2 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_2_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_2_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.zero)

def P_2_2 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.ofCoeffs 1 (fun k => if k = 0 then ScalarExpr.zero else ScalarExpr.one)

def P : MatrixOp 3 ScalarExpr 1 := fun i j =>
  if i.val = 0 then if j.val = 0 then P_0_0 else if j.val = 1 then P_0_1 else P_0_2 else if i.val = 1 then if j.val = 0 then P_1_0 else if j.val = 1 then P_1_1 else P_1_2 else if j.val = 0 then P_2_0 else if j.val = 1 then P_2_1 else P_2_2

def dtOp (A : BoundedDiffOp ScalarExpr 2) : BoundedDiffOp ScalarExpr 3 :=
  BoundedDiffOp.ofCoeffs 3 (fun k => if k = 0 then ScalarExpr.Dt evolution (BoundedDiffOp.coeffNat A 0) else if k = 1 then ScalarExpr.Dt evolution (BoundedDiffOp.coeffNat A 1) else if k = 2 then ScalarExpr.Dt evolution (BoundedDiffOp.coeffNat A 2) else ScalarExpr.zero)

def laxResidual_0_0 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))))

def laxResidual_0_1 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))))

def laxResidual_0_2 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))))

def laxResidual_1_0 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))))

def laxResidual_1_1 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))))

def laxResidual_1_2 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))))

def laxResidual_2_0 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))))

def laxResidual_2_1 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))))

def laxResidual_2_2 : BoundedDiffOp ScalarExpr 3 :=
  (dtOp (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) - ((((BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) - (((BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) (P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))) + (BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) (P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))) + (BoundedDiffOp.composeToBound 3 (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) (P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))))

def laxResidual : MatrixOp 3 ScalarExpr 3 := fun i j =>
  if i.val = 0 then if j.val = 0 then laxResidual_0_0 else if j.val = 1 then laxResidual_0_1 else laxResidual_0_2 else if i.val = 1 then if j.val = 0 then laxResidual_1_0 else if j.val = 1 then laxResidual_1_1 else laxResidual_1_2 else if j.val = 0 then laxResidual_2_0 else if j.val = 1 then laxResidual_2_1 else laxResidual_2_2

def laxCoefficientAt (i : Fin 3) (j : Fin 3) (k : Fin 4) : Prop :=
  ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero

def laxCoefficientCertificate : Prop :=
  ∀ i j k, ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero

theorem laxCoefficientCertificate_indexed :
    ∀ i j k, ScalarExpr.simplify (((laxResidual i j).coeff k)) = ScalarExpr.zero := by
  intro i j k
  have h_i : i.val = 0 ∨ i.val = 1 ∨ i.val = 2 := by omega
  rcases h_i with h_i | h_i | h_i <;>
    have h_j : j.val = 0 ∨ j.val = 1 ∨ j.val = 2 := by omega
  all_goals
    rcases h_j with h_j | h_j | h_j <;>
      have h_k : k.val = 0 ∨ k.val = 1 ∨ k.val = 2 ∨ k.val = 3 := by omega
  all_goals
    rcases h_k with h_k | h_k | h_k | h_k <;>
      simp only [laxResidual, h_i, h_j]
  all_goals
    first
      | have h_k_eq : k = (⟨0, by decide⟩ : Fin 4) := by apply Fin.ext; assumption
      | have h_k_eq : k = (⟨1, by decide⟩ : Fin 4) := by apply Fin.ext; assumption
      | have h_k_eq : k = (⟨2, by decide⟩ : Fin 4) := by apply Fin.ext; assumption
      | have h_k_eq : k = (⟨3, by decide⟩ : Fin 4) := by apply Fin.ext; assumption
    subst k
    native_decide

theorem candidate_satisfies_lax_equation : laxCoefficientCertificate := by
  exact laxCoefficientCertificate_indexed

def selfAdjointResidualL_0_0 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) - (L (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))

def selfAdjointResidualL_0_1 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) - (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))

def selfAdjointResidualL_0_2 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) - (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))

def selfAdjointResidualL_1_0 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) - (L (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))

def selfAdjointResidualL_1_1 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) - (L (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))

def selfAdjointResidualL_1_2 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) - (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))

def selfAdjointResidualL_2_0 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) - (L (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3))

def selfAdjointResidualL_2_1 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) - (L (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3))

def selfAdjointResidualL_2_2 : BoundedDiffOp ScalarExpr 2 :=
  BoundedDiffOp.formalAdjointBounded (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) - (L (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3))

def selfAdjointResidualL : MatrixOp 3 ScalarExpr 2 := fun i j =>
  if i.val = 0 then if j.val = 0 then selfAdjointResidualL_0_0 else if j.val = 1 then selfAdjointResidualL_0_1 else selfAdjointResidualL_0_2 else if i.val = 1 then if j.val = 0 then selfAdjointResidualL_1_0 else if j.val = 1 then selfAdjointResidualL_1_1 else selfAdjointResidualL_1_2 else if j.val = 0 then selfAdjointResidualL_2_0 else if j.val = 1 then selfAdjointResidualL_2_1 else selfAdjointResidualL_2_2

def selfAdjointLCoefficientAt (i : Fin 3) (j : Fin 3) (k : Fin 3) : Prop :=
  ScalarExpr.simplify (((selfAdjointResidualL i j).coeff k)) = ScalarExpr.zero

def selfAdjointLCoefficientCertificate : Prop :=
  ∀ i j k, ScalarExpr.simplify (((selfAdjointResidualL i j).coeff k)) = ScalarExpr.zero

theorem selfAdjointLCoefficientCertificate_indexed :
    ∀ i j k, ScalarExpr.simplify (((selfAdjointResidualL i j).coeff k)) = ScalarExpr.zero := by
  intro i j k
  have h_i : i.val = 0 ∨ i.val = 1 ∨ i.val = 2 := by omega
  rcases h_i with h_i | h_i | h_i <;>
    have h_j : j.val = 0 ∨ j.val = 1 ∨ j.val = 2 := by omega
  all_goals
    rcases h_j with h_j | h_j | h_j <;>
      have h_k : k.val = 0 ∨ k.val = 1 ∨ k.val = 2 := by omega
  all_goals
    rcases h_k with h_k | h_k | h_k <;>
      simp only [selfAdjointResidualL, h_i, h_j]
  all_goals
    first
      | have h_k_eq : k = (⟨0, by decide⟩ : Fin 3) := by apply Fin.ext; assumption
      | have h_k_eq : k = (⟨1, by decide⟩ : Fin 3) := by apply Fin.ext; assumption
      | have h_k_eq : k = (⟨2, by decide⟩ : Fin 3) := by apply Fin.ext; assumption
    subst k
    native_decide

theorem candidate_self_adjoint_L : selfAdjointLCoefficientCertificate := by
  exact selfAdjointLCoefficientCertificate_indexed

def skewAdjointResidualP_0_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) - (-(P (⟨0, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))

def skewAdjointResidualP_0_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) - (-(P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))

def skewAdjointResidualP_0_2 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)) - (-(P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))

def skewAdjointResidualP_1_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨0, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) - (-(P (⟨1, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))

def skewAdjointResidualP_1_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) - (-(P (⟨1, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))

def skewAdjointResidualP_1_2 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)) - (-(P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))

def skewAdjointResidualP_2_0 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨0, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) - (-(P (⟨2, by decide⟩ : Fin 3) (⟨0, by decide⟩ : Fin 3)))

def skewAdjointResidualP_2_1 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨1, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) - (-(P (⟨2, by decide⟩ : Fin 3) (⟨1, by decide⟩ : Fin 3)))

def skewAdjointResidualP_2_2 : BoundedDiffOp ScalarExpr 1 :=
  BoundedDiffOp.formalAdjointBounded (P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)) - (-(P (⟨2, by decide⟩ : Fin 3) (⟨2, by decide⟩ : Fin 3)))

def skewAdjointResidualP : MatrixOp 3 ScalarExpr 1 := fun i j =>
  if i.val = 0 then if j.val = 0 then skewAdjointResidualP_0_0 else if j.val = 1 then skewAdjointResidualP_0_1 else skewAdjointResidualP_0_2 else if i.val = 1 then if j.val = 0 then skewAdjointResidualP_1_0 else if j.val = 1 then skewAdjointResidualP_1_1 else skewAdjointResidualP_1_2 else if j.val = 0 then skewAdjointResidualP_2_0 else if j.val = 1 then skewAdjointResidualP_2_1 else skewAdjointResidualP_2_2

def skewAdjointPCoefficientAt (i : Fin 3) (j : Fin 3) (k : Fin 2) : Prop :=
  ScalarExpr.simplify (((skewAdjointResidualP i j).coeff k)) = ScalarExpr.zero

def skewAdjointPCoefficientCertificate : Prop :=
  ∀ i j k, ScalarExpr.simplify (((skewAdjointResidualP i j).coeff k)) = ScalarExpr.zero

theorem skewAdjointPCoefficientCertificate_indexed :
    ∀ i j k, ScalarExpr.simplify (((skewAdjointResidualP i j).coeff k)) = ScalarExpr.zero := by
  intro i j k
  have h_i : i.val = 0 ∨ i.val = 1 ∨ i.val = 2 := by omega
  rcases h_i with h_i | h_i | h_i <;>
    have h_j : j.val = 0 ∨ j.val = 1 ∨ j.val = 2 := by omega
  all_goals
    rcases h_j with h_j | h_j | h_j <;>
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

end LaxCert.Generated.Matrix3x3Order2Zero
