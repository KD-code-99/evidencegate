# EvidenceGate: tests pass, but the refactor changes meaning

Status: draft, not ready for final submission until actual GitLab Duo and CI runs are recorded. Target: Life After Code / Path A / Supervised Automation. Public source: https://github.com/KD-code-99/evidencegate. Required public GitLab project and live Duo session: pending approved project access. Public video: pending; media/demo-narrated.mp4 demonstrates local software only.

## The problem

Passing unit tests can create false confidence in an arithmetic refactor. In our example, three invoice tests all have free shipping, so changing `units*unit_price+shipping` to `units*(unit_price+shipping)` passes every example while charging shipping once per item.

## What EvidenceGate does

EvidenceGate makes one narrow numerical contract executable. It checks the full symbolic polynomial identity over the declared integer domain, obtains an exact counterexample when the identity changes, and blocks packaging. An equivalent rearrangement produces a package containing the checked source and its evidence. Unsupported code remains blocked.

## Technical implementation

The new MIT checker uses exponent-vector coefficients and an independent sorted-word expansion. Replays bind source, contract and checker hashes. The GitLab CI configuration separates tests, verification, packaging and supervised release. The proposed Duo v1 flow has review, verification and evidence components and reads actual command results; it must not edit the contract or bypass a failed check.

## Automation category

Supervised Automation. The flow is designed to inspect, execute checks and prepare evidence. A person retains the production release decision through the manual CI job. Live deployment and execution must be demonstrated before this text can describe Duo behavior in the past tense.

## Existing-system advantage and new work

Our earlier projects supplied the discipline of explicit domains, retained counterexamples and independent replay. This entry's implementation, tests, interface, CI and flow were created after the hackathon began. No pre-existing non-MIT research engine was copied into this Path A entry.

## Results and limitations

Local tests exercise a wrong refactor with passing examples, actual fail-closed packaging, an equivalent package, unsupported programs, source changes and altered receipts. The check proves the supported expression identity, not arbitrary Python or the correctness of the business specification. A digest is not a signed attestation. The local video is evidence of the product, not of GitLab Duo use.

## AI assistance

Codex assisted with implementation, tests and documentation. The proposed Duo flow is part of the source but has not yet run on the sponsor platform. Final submission must include the approved public GitLab project, actual Duo session/CI links and a public under-three-minute video showing that execution.
