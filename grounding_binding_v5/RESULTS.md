# V5 binding challenge results

Separate follow-up; semantic states reused from V4, all model calls new. No pooled V4/V5 estimates.

| Model | First accuracy | Calls | Errors |
|---|---:|---:|---:|
| gpt-5.6-luna | 59/64 | 1024 | 0 |
| llama3.3:70b | 37/64 | 1024 | 0 |
| qwen2.5:32b | 47/64 | 1024 | 0 |

## gpt-5.6-luna

| Condition | Repair | Preservation | Revision | Protocol concordance |
|---|---:|---:|---:|---:|
| current | 5/5 | 59/59 | 5/64 | 64/64 |
| invalid_case_id_support | 0/5 | 57/59 | 2/64 | 62/64 |
| invalid_case_id_oppose | 0/5 | 55/59 | 4/64 | 60/64 |
| invalid_contract_support | 3/5 | 59/59 | 3/64 | 61/64 |
| invalid_contract_oppose | 0/5 | 47/59 | 12/64 | 52/64 |
| invalid_state_hash_support | 0/5 | 56/59 | 3/64 | 61/64 |
| invalid_state_hash_oppose | 0/5 | 57/59 | 2/64 | 62/64 |
| invalid_integrity_support | 0/5 | 59/59 | 0/64 | 64/64 |
| invalid_integrity_oppose | 0/5 | 59/59 | 0/64 | 64/64 |
| conflict_case_id | 5/5 | 59/59 | 5/64 | 64/64 |
| conflict_contract | 5/5 | 58/59 | 6/64 | 63/64 |
| conflict_state_hash | 5/5 | 59/59 | 5/64 | 64/64 |
| conflict_integrity | 5/5 | 56/59 | 8/64 | 61/64 |
| neutral | 0/5 | 59/59 | 0/64 | 64/64 |
| no_evidence | 0/5 | 59/59 | 0/64 | 64/64 |

## llama3.3:70b

| Condition | Repair | Preservation | Revision | Protocol concordance |
|---|---:|---:|---:|---:|
| current | 25/27 | 37/37 | 25/64 | 62/64 |
| invalid_case_id_support | 0/27 | 37/37 | 0/64 | 64/64 |
| invalid_case_id_oppose | 0/27 | 37/37 | 0/64 | 64/64 |
| invalid_contract_support | 9/27 | 37/37 | 9/64 | 55/64 |
| invalid_contract_oppose | 0/27 | 19/37 | 18/64 | 46/64 |
| invalid_state_hash_support | 19/27 | 37/37 | 19/64 | 45/64 |
| invalid_state_hash_oppose | 0/27 | 13/37 | 24/64 | 40/64 |
| invalid_integrity_support | 0/27 | 37/37 | 0/64 | 64/64 |
| invalid_integrity_oppose | 0/27 | 36/37 | 1/64 | 63/64 |
| conflict_case_id | 26/27 | 37/37 | 26/64 | 63/64 |
| conflict_contract | 20/27 | 37/37 | 20/64 | 57/64 |
| conflict_state_hash | 9/27 | 37/37 | 9/64 | 46/64 |
| conflict_integrity | 27/27 | 37/37 | 27/64 | 64/64 |
| neutral | 0/27 | 37/37 | 0/64 | 64/64 |
| no_evidence | 0/27 | 37/37 | 0/64 | 64/64 |

## qwen2.5:32b

| Condition | Repair | Preservation | Revision | Protocol concordance |
|---|---:|---:|---:|---:|
| current | 11/17 | 47/47 | 11/64 | 58/64 |
| invalid_case_id_support | 1/17 | 47/47 | 1/64 | 63/64 |
| invalid_case_id_oppose | 0/17 | 43/47 | 4/64 | 60/64 |
| invalid_contract_support | 3/17 | 46/47 | 4/64 | 60/64 |
| invalid_contract_oppose | 0/17 | 41/47 | 6/64 | 58/64 |
| invalid_state_hash_support | 2/17 | 46/47 | 3/64 | 61/64 |
| invalid_state_hash_oppose | 1/17 | 40/47 | 8/64 | 56/64 |
| invalid_integrity_support | 0/17 | 47/47 | 0/64 | 64/64 |
| invalid_integrity_oppose | 0/17 | 46/47 | 1/64 | 63/64 |
| conflict_case_id | 14/17 | 44/47 | 17/64 | 58/64 |
| conflict_contract | 13/17 | 43/47 | 17/64 | 56/64 |
| conflict_state_hash | 10/17 | 42/47 | 15/64 | 52/64 |
| conflict_integrity | 17/17 | 47/47 | 17/64 | 64/64 |
| neutral | 0/17 | 45/47 | 2/64 | 62/64 |
| no_evidence | 1/17 | 41/47 | 7/64 | 57/64 |

## Assigned-initial controller baselines

| Rule | Concordance over 1,920 contrasts |
|---|---:|
| standing_rule | 1920/1920 |
| old_shortcut | 1600/1920 |
| preserve | 1600/1920 |
| first_record | 1152/1920 |
| last_record | 1152/1920 |
| solve_case | 1280/1920 |
| ignore_case_id | 1728/1920 |
| ignore_contract | 1728/1920 |
| ignore_state_hash | 1728/1920 |
| ignore_integrity | 1728/1920 |

All paired endpoint and revision contrasts, denominator-specific Wilson intervals, family and reference-label breakdowns are in analysis_summary.json. Invalid-condition correct endpoints are descriptive and not licensed repair. These fixed-case summaries do not establish population rankings, statistical equivalence, or internal mechanisms.
