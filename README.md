# Structured Irritation: Current Experimental Data

**Selective Answerability and Case-Bound Evidence**

The study evaluates whether competent evidence repairs an incorrect commitment or preserves a correct one, and whether records without standing leave the commitment unchanged. Case identity, contract, state hash, and integrity are manipulated independently.

## Evaluation

Each configuration contributes 64 first responses and 960 continuations across fifteen paired conditions. Each actual first response is fixed across all conditions: **3,072 calls** across Qwen 2.5 32B, Llama 3.3 70B, and GPT-5.6 Luna. Four task families cover type validation, date intervals, URL conversion, and synthetic regional policy.

[The acquisition archive](grounding_binding_v5/) contains the protocol, cases, prompts, semantic reference implementation, model settings, raw observations, primary analysis, and checksums. [Results](grounding_binding_v5/RESULTS.md) report the condition-level outcomes.

[Supplementary descriptive analysis](supplementary_analysis/) applies the controller rules to observed first responses and reports accuracy by reference label and task family. It distinguishes corrections from preservation and identifies the composition of repair opportunities. This analysis is post-collection; the acquisition files remain frozen.

## Verification

From the repository root, without new model calls:

```sh
python3 grounding_binding_v5/verify_archive.py
python3 supplementary_analysis/observed_baselines.py
```

Verify the acquisition archive's files:

```sh
cd grounding_binding_v5
shasum -a 256 -c SHA256SUMS
```

The experiment measures application of explicit admissibility rules. Each configuration has one observed continuation per case and condition. Luna's five initial errors all have reference label B; its observed repair result concerns A-to-B transitions.
