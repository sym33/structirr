# Field-isolated binding challenge V5

V5 is a separately specified follow-up to the shortcut identified in V4. It reuses the 64 semantic task states, with new case/contract/record identifiers and fresh model-generated first responses. Fifteen continuations branch each frozen first response. Planned size: 1,024 calls per configuration, 3,072 overall. Do not pool V4 and V5 outcomes or count continuations as independent cases.

## Reproduce the audit

Run from this directory:

```sh
python3 -m unittest test_design -v
sha256sum -c FROZEN_SHA256SUMS
python3 analyze.py
python3 verify_archive.py
```

`PROTOCOL.md` describes the design and planned analyses. `FROZEN_SHA256SUMS` fixes design, semantic reference, tasks, protocol, tests, runner, launch scripts and analysis before V5 model calls. This is prospective specification of a follow-up informed by V4, not external preregistration. `analysis_summary.json` includes all outcomes, paired contrasts and controller baselines; `RESULTS.md` is generated from it. Completion is determined by per-model status files, total counts, and retained errors, not by the presence of a result file alone.

`test_design.py` checks semantic references and label swaps, balance, single-field interventions, and failure of specified shortcuts/field-omission rules. Record-renaming/permutation invariance is a reference-controller test, not an additional model condition. All nonempty conditions contain two records; no evidence contains none.

The full-rule baseline uses all fields. The four ablations each omit exactly one field. Assigned A/B initial actions for baselines are not model observations. Supporting-invalid records recommend the semantically correct action but require preserving the actual first choice; opposing-invalid records recommend the wrong action and likewise require preservation. Thus endpoint correctness and protocol conformity must be kept separate.

## Observations and execution

`results/<model>/observations.jsonl` retains prompts, raw responses, invocation options, traces, errors and first-response hashes. Existing rows are resumed, not repeated, and there are no response-dependent retries. Hosted answer files are retained alongside event traces; no credentials are included. `model_inventory.json`, version files and service logs record the environment. Model aliases may change; identical regeneration is not promised.

The archived `launch_remote.py` is specific to the original server and starts a dedicated local service plus the hosted and local runners. The local runner stops only the service started for this experiment. To collect new observations, use a fresh directory without `results`, ensure compatible authenticated model access and inspect server-specific executable paths first. No new calls are needed to audit the archived results.

## Scope

The challenge separates the specified V4 shortcut and each one-field omission from the full standing rule. It cannot eliminate every possible shortcut or identify internal reasoning. Direct action recommendations, explicit validity flags, supplied hash anchors, a small reused semantic sample, and the lack of deferral limit interpretation. Success does not establish independent provenance verification or domain expertise.

`verify_archive.py` is a post-collection integrity check, separate from the prospectively frozen analysis. It cross-checks tabulated counts against raw rows, verifies frozen hashes, and checks local prompt sizes and recorded invocation fields. It introduces no new model calls or inferential analyses.
