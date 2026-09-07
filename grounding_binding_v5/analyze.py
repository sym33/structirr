"""Prospectively specified V5 audit and descriptive paired outcomes."""
import collections,hashlib,json,math
from pathlib import Path
from design import CONDITIONS,FIELDS,baseline,target,digest,first_prompt,second_prompt
from reference import reference
ROOT=Path(__file__).resolve().parent

def frac(k,n):return {'k':k,'n':n,'rate':k/n if n else None}
def wilson(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n;m=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,m-h),min(1,m+h)]
def pair(values):
    v=list(values);a=sum(x and not y for x,y in v);b=sum(y and not x for x,y in v)
    return {'n':len(v),'condition_only':a,'control_only':b,'difference':(a-b)/len(v) if v else None}
def main():
    tasks=json.loads((ROOT/'tasks.json').read_text());lookup={t['case']['case_id']:t for t in tasks}
    for t in tasks:assert reference(t['case'])==t['gold']
    out={'design':'V5; 64 reused semantic states, new identifiers and fresh first calls; 15 continuations per case','models':{},'baselines':{}}
    for kind in ['standing_rule','old_shortcut','preserve','first_record','last_record','solve_case']+['ignore_'+f for f in FIELDS]:
        out['baselines'][kind]={c:frac(sum(baseline(t,a,c,kind)==target(t,a,c) for t in tasks for a in 'AB'),128) for c in CONDITIONS}
    for path in sorted((ROOT/'results').glob('*/observations.jsonl')):
        rows=[json.loads(l) for l in path.read_text().splitlines()]
        assert len({(r['case_id'],r['stage'],r.get('condition')) for r in rows})==len(rows)
        first={r['case_id']:r for r in rows if r['stage']=='first'};second={}
        for r in rows:
            t=lookup[r['case_id']];assert r['gold']==reference(t['case'])
            assert hashlib.sha256(r['prompt'].encode()).hexdigest()==r['prompt_sha256']
            if r['stage']=='first':assert r['prompt']==first_prompt(t)
            else:
                f=first[r['case_id']];assert r['first_response']==f['response'] and r['first_response_sha256']==digest(f['response'])
                assert r['prompt']==second_prompt(t,f['response'],r['condition'])
                if not r['error']:second[r['case_id'],r['condition']]=r
        good={cid:f for cid,f in first.items() if not f['error']}
        result={'calls':len(rows),'planned_calls':1024,'errors':sum(bool(r['error']) for r in rows),'tool_events':sum(len(r['tool_events']) for r in rows),'first_accuracy':frac(sum(f['response']['action']==f['gold'] for f in good.values()),len(good)),'first_by_family':{},'first_by_reference_label':{},'conditions':{},'paired':{}}
        for fam in ('type','date','url','policy'):
            rr=[f for f in good.values() if f['family']==fam];result['first_by_family'][fam]={'accuracy':frac(sum(f['response']['action']==f['gold'] for f in rr),len(rr)),'actions':dict(collections.Counter(f['response']['action'] for f in rr))}
        for a in 'AB':
            rr=[f for f in good.values() if f['gold']==a];result['first_by_reference_label'][a]=frac(sum(f['response']['action']==a for f in rr),len(rr))
        for c in CONDITIONS:
            rr=[r for (cid,cond),r in second.items() if cond==c]
            wrong=[r for r in rr if r['first_response']['action']!=r['gold']];right=[r for r in rr if r['first_response']['action']==r['gold']]
            repair=sum(r['response']['action']==r['gold'] for r in wrong);pres=sum(r['response']['action']==r['gold'] for r in right)
            result['conditions'][c]={'repair':frac(repair,len(wrong)),'preservation':frac(pres,len(right)),'revision':frac(sum(r['response']['action']!=r['first_response']['action'] for r in rr),len(rr)),'concordance':frac(sum(r['response']['action']==target(lookup[r['case_id']],r['first_response']['action'],c) for r in rr),len(rr)),'repair_wilson95':wilson(repair,len(wrong)),'preservation_wilson95':wilson(pres,len(right))}
            controls=['neutral','no_evidence']+(['current'] if c.startswith(('invalid_','conflict_')) else [])
            for control in controls:
                if c==control:continue
                ids=[cid for cid in good if (cid,c) in second and (cid,control) in second]
                groups={}
                for group,initial_correct in [('initially_wrong',False),('initially_correct',True)]:
                    subset=[cid for cid in ids if (good[cid]['response']['action']==good[cid]['gold'])==initial_correct]
                    groups[group]=pair((second[cid,c]['response']['action']==good[cid]['gold'],second[cid,control]['response']['action']==good[cid]['gold']) for cid in subset)
                groups['revision']=pair((second[cid,c]['response']['action']!=good[cid]['response']['action'],second[cid,control]['response']['action']!=good[cid]['response']['action']) for cid in ids)
                result['paired'][c+' vs '+control]=groups
        out['models'][path.parent.name]=result
    (ROOT/'analysis_summary.json').write_text(json.dumps(out,indent=2)+'\n')
    lines=['# V5 binding challenge results','','Separate follow-up; semantic states reused from V4, all model calls new. No pooled V4/V5 estimates.','','| Model | First accuracy | Calls | Errors |','|---|---:|---:|---:|']
    for model,m in out['models'].items():lines.append(f"| {model} | {m['first_accuracy']['k']}/{m['first_accuracy']['n']} | {m['calls']} | {m['errors']} |")
    for model,m in out['models'].items():
        lines+=['','## '+model,'','| Condition | Repair | Preservation | Revision | Protocol concordance |','|---|---:|---:|---:|---:|']
        for c,v in m['conditions'].items():lines.append('| '+c+' | '+' | '.join(f"{v[k]['k']}/{v[k]['n']}" for k in ('repair','preservation','revision','concordance'))+' |')
    lines+=['','## Assigned-initial controller baselines','','| Rule | Concordance over 1,920 contrasts |','|---|---:|']
    for kind,cs in out['baselines'].items():lines.append(f"| {kind} | {sum(v['k'] for v in cs.values())}/1920 |")
    lines+=['','All paired endpoint and revision contrasts, denominator-specific Wilson intervals, family and reference-label breakdowns are in analysis_summary.json. Invalid-condition correct endpoints are descriptive and not licensed repair. These fixed-case summaries do not establish population rankings, statistical equivalence, or internal mechanisms.']
    (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({m:{k:v[k] for k in ('calls','errors','first_accuracy')} for m,v in out['models'].items()}))
if __name__=='__main__':main()
