# LAXCERT Visual Console

The LAXCERT console is a local browser UI for inspecting candidate inputs, proof artifacts, job history, and explicit proof commands. It is intentionally repository-local and runs on `127.0.0.1` by default.

Start it from the repository root:

```bash
python -m laxforge_laxcert.console_server --repo-root .
```

or, after installing the package:

```bash
laxcert-console --repo-root .
```

Then open:

```text
http://127.0.0.1:8765
```

The console currently exposes these operator commands:

- `Validate Schema` resolves an internal candidate JSON, external LAXFORGE artifact directory, or manifest and runs schema plus semantic validation.
- `Certify Candidate` normalizes the candidate, emits Lean, runs Lake, and writes `artifacts/<candidate_id>/proof-status.json`.
- `Certify Expected Failure` passes only when a candidate is rejected or fails to prove.
- `Lake Build` runs `lake -R build LaxCert`.
- `Pytest` runs the Python regression suite.

The UI reads candidate JSON from `candidates/*.json` and committed artifact inputs from `artifacts/*/candidate.json`. The command input accepts repository-relative paths such as `candidates/toy_lax_zero.json` and absolute paths to externally produced LAXFORGE artifact directories.
