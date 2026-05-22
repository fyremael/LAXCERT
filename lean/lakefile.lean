import Lake
open Lake DSL

package «laxcert» where
  -- Add package configuration here.

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.29.1"

@[default_target]
lean_lib LaxCert where
  roots := #[`LaxCert]
