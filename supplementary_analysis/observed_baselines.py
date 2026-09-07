"""Post-collection descriptive comparisons; frozen acquisition files remain unchanged."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'grounding_binding_v5'))
from design import baseline, target, CONDITIONS
kinds=['standing_rule','preserve','solve_case','first_record','last_record','ignore_case_id','ignore_contract','ignore_state_hash','ignore_integrity']
tasks={t['case']['case_id']:t for t in json.loads((ROOT/'grounding_binding_v5/tasks.json').read_text())}
out={}
for model in ['qwen2.5:32b','llama3.3:70b','gpt-5.6-luna']:
 rows=[json.loads(s) for s in (ROOT/'grounding_binding_v5/results'/model/'observations.jsonl').read_text().splitlines()]
 first={r['case_id']:r['response']['action'] for r in rows if r['stage']=='first'}
 assert len(first)==64
 counts={k:sum(baseline(tasks[c],a,g,k)==target(tasks[c],a,g) for c,a in first.items() for g in CONDITIONS) for k in kinds}
 transitions={}
 for g in CONDITIONS:
  rr=[r for r in rows if r['stage']!='first' and r['condition']==g]
  assert len(rr)==64
  wrong=[r for r in rr if first[r['case_id']]!=r['gold']];right=[r for r in rr if first[r['case_id']]==r['gold']]
  transitions[g]={'correction':sum(r['response']['action']==r['gold'] for r in wrong),'wrong_n':len(wrong),'preservation':sum(r['response']['action']==r['gold'] for r in right),'right_n':len(right),'concordance':sum(r['response']['action']==target(tasks[r['case_id']],first[r['case_id']],g) for r in rr)}
 counts['observed_model']=sum(v['concordance'] for v in transitions.values())
 assert counts['standing_rule']==960
 first_rows=[r for r in rows if r['stage']=='first']
 strata={}
 for field,values in [('family',['type','date','url','policy']),('gold',['A','B'])]:
  strata[field]={}
  for value in values:
   subset=[r for r in first_rows if r[field]==value]
   strata[field][value]={'correct':sum(r['response']['action']==r['gold'] for r in subset),'n':len(subset)}
  assert sum(v['n'] for v in strata[field].values())==64
  assert sum(v['correct'] for v in strata[field].values())==transitions['current']['right_n']
 out[model]={'n':960,'baselines':counts,'transitions':transitions,'first_strata':strata}
p=Path(__file__).with_name('observed_baselines.json');p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({m:v['baselines'] for m,v in out.items()},indent=2))
