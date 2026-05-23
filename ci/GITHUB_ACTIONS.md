# CI Plan

## Required jobs

### `schema`

Validate all candidate JSON files against `schemas/laxcert_candidate.schema.json`.

### `lean-core`

Run:

```bash
lake build LaxCert
```

### `lean-generated-positive`

Run:

```bash
lake build LaxCert.Generated
```

### `lean-generated-negative`

Build intentionally false candidates and assert failure.

Pseudo-shell:

```bash
if lake build LaxCert.Generated.FalseCandidate; then
  echo "False candidate unexpectedly proved"
  exit 1
else
  echo "False candidate correctly failed"
fi
```

### `no-sorry`

Run a crude no-admission check:

```bash
! grep -R "sorry\|admit\|axiom" lean/LaxCert
```

Later replace with theorem-level axiom auditing.

### `deterministic-emission`

Regenerate Lean from JSON and check that generated files match the committed hash.

The executable workflow checks the committed generated theorem modules and
artifact hashes after regenerating the positive candidates:

```bash
git diff --exit-code -- \
  lean/LaxCert/Generated/ToyLaxZero.lean \
  lean/LaxCert/Generated/Matrix2x2Zero.lean \
  lean/LaxCert/Generated/Matrix2x2OffDiagonalZero.lean \
  lean/LaxCert/Generated/AKNSD2TransportZero.lean \
  lean/LaxCert/Generated/LaxforgeAKNSD2TransportZero.lean \
  lean/LaxCert/Generated/Matrix3x3Order2Zero.lean \
  artifacts/ToyLaxZero/generated.lean \
  artifacts/ToyLaxZero/generated.hash \
  artifacts/Matrix2x2Zero/generated.lean \
  artifacts/Matrix2x2Zero/generated.hash \
  artifacts/Matrix2x2OffDiagonalZero/generated.lean \
  artifacts/Matrix2x2OffDiagonalZero/generated.hash \
  artifacts/AKNSD2TransportZero/generated.lean \
  artifacts/AKNSD2TransportZero/generated.hash \
  artifacts/LaxforgeAKNSD2TransportZero/generated.lean \
  artifacts/LaxforgeAKNSD2TransportZero/generated.hash \
  artifacts/Matrix3x3Order2Zero/generated.lean \
  artifacts/Matrix3x3Order2Zero/generated.hash
```

## GitHub Actions sketch

```yaml
name: laxcert-ci

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lean:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install elan
        run: |
          curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
          echo "$HOME/.elan/bin" >> $GITHUB_PATH
      - name: Build Lean core
        run: lake build LaxCert
      - name: No sorry/admit/axiom
        run: '! grep -R "sorry\|admit\|axiom" lean/LaxCert'
```
