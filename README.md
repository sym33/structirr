# Structured Irritation: Experimental Data

This repository contains the data and analysis for **Selective Answerability and Case-Bound Evidence**. The experiment tests whether models repair incorrect answers with competent evidence, preserve correct answers, and resist redirection by records that lack authority over the active case.

## Study at a glance

- **Models:** Qwen 2.5 32B, Llama 3.3 70B, and GPT-5.6 Luna.
- **Design:** 64 cases per model, each with one first response fixed across 15 evidence conditions; **3,072 model calls** in total.
- **Tasks:** type validation, date intervals, URL conversion, and synthetic regional policy.
- **Evidence checks:** case identity, contract, state hash, and integrity.

## What the two folders contain

Both folders belong to **the same experiment** and use the same observations.

| Folder | Contents |
| --- | --- |
| [`grounding_binding_v5/`](grounding_binding_v5/) | Raw model responses, cases and prompts, protocol, model settings, reference validator, condition-level results, and file checksums. |
| [`supplementary_analysis/`](supplementary_analysis/) | Controller comparisons on the actual first responses, correction and preservation counts, and first-stage accuracy by task family and answer label. |

Start with the [experiment results](grounding_binding_v5/RESULTS.md), the [protocol](grounding_binding_v5/PROTOCOL.md), or the [additional analysis results](supplementary_analysis/observed_baselines.json).

## Verify and reproduce

Run from the repository root with Python 3. These commands use the included observations and make no model calls:

```sh
python3 grounding_binding_v5/verify_archive.py
python3 supplementary_analysis/observed_baselines.py
```

Check file integrity:

```sh
(cd grounding_binding_v5 && shasum -a 256 -c SHA256SUMS)
```
