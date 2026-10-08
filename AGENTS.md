# EvidenceGate contract

This is a new MIT numerical verification project. Work only on its declared sample. Integer-domain arithmetic and pure return expressions are the supported semantics. Never present ordinary unit-test passes as universal correctness.

Run `python -B -m unittest discover -s tests -v` and `python -B -m evidencegate audit --out artifacts/contract.json`. A blocked or unsupported contract prevents packaging and release. Keep contracts, verifier source and tests independent of proposed sample changes. Do not weaken them to admit a refactor. The release CI job requires a human decision.
