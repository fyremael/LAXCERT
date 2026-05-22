namespace LaxCert

/-- Field names supported by the phase 1 scalar jet algebra. -/
inductive FieldName where
  | u
  | p
  | q
  deriving DecidableEq, Repr

/-- A jet variable is a field together with its spatial derivative order.

For example, `JetVar.mk FieldName.p 1` represents `p_x`. -/
structure JetVar where
  field : FieldName
  order : Nat
  deriving DecidableEq, Repr

namespace JetVar

/-- Spatial derivation shifts a jet variable to the next derivative order. -/
def dx (v : JetVar) : JetVar :=
  { v with order := v.order + 1 }

end JetVar

namespace FieldName

def baseJet (field : FieldName) : JetVar :=
  { field, order := 0 }

end FieldName

end LaxCert
