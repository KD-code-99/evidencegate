# EvidenceGate: stop billing refactors that green tests miss

Status: local project creation draft. Target: Life After Code / Path A / Supervised Automation. The working application, public GitHub source and downloadable build are complete. An approved hackathon GitLab project, actual Duo session, GitLab-hosted pipeline results and public video URL remain pending. This document does not establish Devpost project creation, eligibility agreement or final submission.

## One-line summary

EvidenceGate catches a billing change that passes ordinary tests, blocks its package, and binds an equivalent revision to evidence that the running service rechecks.

## Problem

A developer changes `units * unit_price + shipping` to `units * (unit_price + shipping)`. All three example tests pass because they use zero shipping. For `units=2`, `unit_price=1`, `shipping=1`, the agreed formula returns **3**, but the refactor returns **4**: shipping is charged once per item.

A green example suite is insufficient evidence that this arithmetic change preserves the stated billing contract. The contract must remain independent of the proposed revision.

## Solution and why it matters

EvidenceGate checks the declared integer-polynomial identity and returns an exact counterexample when the expressions differ. The wrong refactor passes the example suite but receives a blocked contract verdict, so packaging fails. An equivalent revision, `shipping + unit_price * units`, passes the exact contract and produces an actual ZIP containing the checked billing source, contract and receipt.

The workflow continues beyond a verdict. EvidenceGate extracts that ZIP, replays its embedded evidence, starts an owned local billing HTTP service and executes canaries. Changing the staged source causes both `/health` and `/invoice` to return HTTP 503. Restoring the checked source permits the health check again. A person retains the production release decision.

This gives a developer a reproducible reason to stop an incorrect numerical change and an inspectable path for an equivalent change. The example is deliberately narrow enough for the complete behavior to be checked. I do not claim measured adoption, financial savings or correctness of arbitrary application code.

## Key features and architecture

- **Independent exact checking:** the contract and actual expression expand into exponent-vector coefficient maps. A second expansion uses sorted variable words and must agree. Zero residual coefficients establish the supported identity over integer arguments; a nonzero residual produces an exact witness on a degree-complete grid.
- **Evidence tied to the artifact:** receipts bind source, contract and checker hashes. Replay recomputes the obligation against current files. Altered receipts or later source changes cannot unlock packaging.
- **Executed package and staging gates:** the application creates a real verified ZIP and runs its extracted billing service. The retained local acceptance covers startup, 18 billing HTTP canaries, drift rejection on two endpoints and recovery: **22 checks**.
- **A clear human decision:** the configured CI stages are test, verify, package, staging and a manual `supervised_release`. A failed verification prevents downstream packaging. This configuration has not yet executed in GitLab.

The Python 3.12 application has no third-party runtime dependencies. Its browser interface uses the actual checker, packaging and staging workflows. It is an executable local product, not a prepared transcript.

## How I used AI

The proposed GitLab Duo custom v1 flow has review, verification and evidence components. It is designed to inspect the sample change, run the checks and preserve their actual results. It must not edit the contract to obtain a pass or bypass a blocked verdict. The flow configuration is present and reviewed against the documented schema; **no live Duo execution is claimed**.

Supervised Automation is the intended category. The agent prepares reviewable evidence while a human retains the manual release decision. The final platform demonstration must show a real Duo session and visible GitLab pipeline outcomes for both the wrong and equivalent revisions.

## How I used Codex and what is new

I used Codex to help implement the checker, receipt replay, interface, package/staging workflow, tests, CI configuration and documentation. Correctness claims depend on executed exact checks and independent controls, not generated explanations.

My earlier projects supplied experience with explicit domains, retained counterexamples and replay. All application, checker and flow code in this fresh MIT project was written on **8 October 2026**. No pre-existing NOETHER-FORGE engine or private research archive was copied into the entry. [New-work record](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/NEW_WORK.md).

## Testing instructions and retained results

Download and extract the [v0.1.0 complete source/test build](https://github.com/KD-code-99/evidencegate/releases/download/v0.1.0/evidencegate-test-build.zip). With Python 3.12 or newer, run from the extracted folder:

```sh
python -B -m evidencegate serve
```

Open `http://127.0.0.1:4187`. Select **Wrong refactor** to see the passing examples, exact counterexample and blocked package. Select **Equivalent refactor** to download a checked ZIP and run its staging checks. Select the unsupported example to verify that it stays blocked.

The command-line path is also reproducible:

```sh
python -B -m unittest discover -s tests -v
python -B -m evidencegate audit --out artifacts/contract.json
python -B -m evidencegate replay --receipt artifacts/contract.json
python -B -m evidencegate package --receipt artifacts/contract.json
python -B -m evidencegate staging --receipt artifacts/contract.json --out artifacts/staging.json
```

**13 acceptance tests passed.** They cover the misleading example tests, independent witness, exact equivalence, unsupported code, tampered receipts, changed source, real ZIP packaging, actual HTTP requests and staging/drift behavior. The staging test asserts all **22 checks** and 18 canaries pass; these are local checks, not 22 GitLab jobs.

Direct evidence:

- [Executed test output](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/evidence/tests.txt) and [execution record](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/evidence/validation.json).
- [Actual browser workflow and responsive checks](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/evidence/browser-validation.json).
- [Staging acceptance assertions](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/tests/test_staging.py) and [executed workflow implementation](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/evidencegate/staging.py).
- [Configured GitLab pipeline](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/.gitlab-ci.yml) and [Duo activation/demo instructions](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/docs/duo-demo.md), both awaiting sponsor-platform execution.

## Public repository and demo

Public source: [KD-code-99/evidencegate](https://github.com/KD-code-99/evidencegate). License: [MIT](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/LICENSE). Downloadable build: [v0.1.0 release](https://github.com/KD-code-99/evidencegate/releases/tag/v0.1.0).

Required hackathon GitLab project: **pending approved contributor project access**. Actual Duo session URL and GitLab pipeline URLs: **pending**. Public application endpoint: none; the current reproducible demonstration uses the source/test build on localhost.

## Demo video and screenshot shot list

The [English narrated local recording](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/media/demo-narrated.mp4) is prepared and under three minutes. It records the working local product with visibly adjusted playback timing. It does not show a live Duo session. Public video hosting and the platform-execution recording remain pending.

Lead the final platform video with the passing free-shipping tests and the **3 versus 4** counterexample. Then show the real Duo commands and pipeline verdict, equivalent revision, downloadable package, executed staging/drift result and manual release decision. Retain the original local recording as supporting evidence.

Prepared screenshots show the [blocked refactor](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/media/02-blocked-refactor.png), [verified package](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/media/03-verified-package.png), [unsupported program](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/media/04-unsupported.png) and [staging/drift gate](https://github.com/KD-code-99/evidencegate/blob/codex/gitlab-evidencegate/media/05-staging-drift.png). Platform screenshots must come from the actual Duo session and pipeline once available.

## Known limitations

The supported source is one undecorated positional function with a single bounded integer-polynomial return expression. Floats, division, calls, decorators, defaults, branches and module effects remain unsupported and block packaging. The check proves equivalence to the declared contract; it does not prove that the business specification is correct or certify arbitrary Python. A receipt digest is an integrity binding, not a signed attestation.

The service executes in ephemeral local staging. No cloud deployment, production release or live sponsor automation is claimed. The prepared configuration and local video cannot substitute for actual GitLab Duo and CI evidence.

## Submission readiness and official form fields

This packet is ready for local review and later mapping into the live project form. Official live form fields and IDs have not been verified; no personal eligibility or rules agreement is filled in here. The remaining material gaps are approved GitLab access, actual Duo/pipeline runs with inspectable links and public video hosting. Final submission remains a separate step after those facts are reviewable.
