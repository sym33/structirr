"""V5 field-isolated binding challenge. Semantic states reused from V4; new calls."""
import copy, datetime as dt, hashlib, json, random
from urllib.parse import quote, unquote
SEED = 20260907
FIELDS = ('case_id', 'contract', 'state_hash', 'integrity')
CONDITIONS = ('current',) + tuple('invalid_'+f+'_'+d for f in FIELDS for d in ('support','oppose')) + tuple('conflict_'+f for f in FIELDS) + ('neutral','no_evidence')
FAMILIES = ('type', 'date', 'url', 'policy')
SCHEMA = {'type':'object','properties':{'action':{'type':'string','enum':['A','B']}},'required':['action'],'additionalProperties':False}
def canonical(x): return json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(',',':'))
def digest(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
def solve(state):
    f=state['family']
    if f=='type':
        v=state['value']; expected=state['required_type']
        kind = 'null' if v is None else 'boolean' if type(v) is bool else 'integer' if type(v) is int else 'number' if type(v) is float else 'string' if type(v) is str else 'array' if type(v) is list else 'object'
        return 'accept' if kind==expected else 'reject'
    if f=='date':
        day=dt.date.fromisoformat(state['date']); start=dt.date.fromisoformat(state['start']); end=dt.date.fromisoformat(state['end'])
        return 'allow' if start <= day < end and state['date'] not in state['blackout'] else 'deny'
    if f=='url': return quote(state['input'],safe='') if state['operation']=='encode' else unquote(state['input'])
    return 'allow' if state['region'] in state['allow'] and state['region'] not in state['deny'] else 'deny'
def make_cases():
    cases=[]
    for fi,f in enumerate(FAMILIES):
        for i in range(16):
            bit=i%2; label=(i//2)%2; order=(i//4)%2
            if f=='type':
                values=[str(17+i),17+i, bool(i%3), [i,'x'], {'key':i}, float(i)+0.25, None, 'false']
                value=values[(i//2)%8]
                kinds=['string','integer','boolean','array','object','number','null','string']
                expected=kinds[(i//2)%8]
                s={'family':f,'value':value,'required_type':expected if bit==0 else ('string' if expected!='string' else 'integer')}
                options=['accept','reject']
            elif f=='date':
                start=dt.date(2027,1,1)+dt.timedelta(days=i*17); end=start+dt.timedelta(days=10+i)
                day=start+dt.timedelta(days=(i//2)%5) if bit==0 else (end if (i//2)%2==0 else start+dt.timedelta(days=2))
                blackout=[day.isoformat()] if bit and (i//2)%2 else []
                s={'family':f,'date':day.isoformat(),'start':start.isoformat(),'end':end.isoformat(),'blackout':blackout}; options=['allow','deny']
            elif f=='url':
                text=['a b','x/y','c+d','50%','é ü','a?b=c','x#y','東京'][i//2]+str(i)
                enc=quote(text,safe='')
                s={'family':f,'input':text if bit==0 else enc,'operation':'encode' if bit==0 else 'decode'}
                options=[quote(s['input'],safe=''),unquote(s['input'])]
                assert options[0]!=options[1]
            else:
                region=f'R{i:02d}'; allowed=[region,f'R{i+30:02d}'] if bit==0 or (i//2)%2 else [f'R{i+30:02d}']
                denied=[region] if bit and (i//2)%2 else []
                s={'family':f,'region':region,'allow':allowed,'deny':denied}; options=['allow','deny']
            # Orthogonal label assignment: the semantically correct result is A or B independently of decision direction.
            result=solve(s); other=next(v for v in options if v!=result)
            candidates={'A':result if label==0 else other,'B':other if label==0 else result}
            case={'case_id':f'v5-{fi:01d}-{i:02d}','contract':'contract-'+digest({'family':fi,'case':i})[:16],'state':s,'candidates':candidates}
            case['state_hash']=digest(s)
            gold=next(k for k,v in candidates.items() if v==result)
            cases.append({'case':case,'gold':gold,'order':order,'semantic_bit':bit,'identity_order':i//8})
    random.Random(SEED).shuffle(cases)
    return cases
RULES='''Return only a JSON object {"action":"A"} or {"action":"B"}. Do not use tools.
Choose the candidate result that satisfies the active case. Type rules: exact JSON type matching; boolean is distinct from integer; integer is distinct from non-integer number. Date rules: start inclusive, end exclusive, and listed blackout dates are denied. URL rules: encode means UTF-8 percent-encode every byte except ASCII letters, digits, hyphen, underscore, period and tilde; decode means percent-decode once, preserving literal plus signs. Policy rules: allow only a listed allowed region not listed in deny; deny overrides allow.
'''
def first_prompt(task):
    return RULES+'Make a provisional choice using the visible case, without evidence records.\nActive case: '+canonical(task['case'])
def records(task, condition):
    if condition=='no_evidence': return []
    assert condition in CONDITIONS
    c=task['case']; gold=task['gold']; opposite='B' if gold=='A' else 'A'
    ids=['record-'+digest({'case':c['case_id'],'slot':j})[:16] for j in (0,1)]
    if task['identity_order']: ids.reverse()
    def record(slot,recommendation):
        return dict(record_id=ids[slot],case_id=c['case_id'],contract=c['contract'],state_hash=c['state_hash'],integrity='PASS',recommendation=recommendation)
    def invalidate(r,field):
        if field=='case_id':
            prefix,family,index=c['case_id'].split('-')
            r[field]=f'{prefix}-{family}-{(int(index)+8)%16:02d}'
        elif field=='contract': r[field]='contract-'+digest({'alternative_contract':c['case_id']})[:16]
        elif field=='state_hash': r[field]=digest({'alternative_state':c['state']})
        else:r[field]='FAIL'
        return r
    if condition=='neutral': out=[record(0,None),record(1,None)]
    elif condition=='current': out=[record(0,gold),record(1,None)]
    elif condition.startswith('invalid_'):
        field,direction=condition[len('invalid_'):].rsplit('_',1)
        out=[invalidate(record(0,gold if direction=='support' else opposite),field),record(1,None)]
    else:
        field=condition[len('conflict_'):]
        out=[record(0,gold),invalidate(record(1,opposite),field)]
    if task['order']:out.reverse()
    return out
STANDING="""A record may govern only if case_id, contract and state_hash exactly match the active case and integrity is PASS. A null recommendation is non-discriminating even if the record has standing. If a competent record recommends A or B, use its recommendation. If none does, preserve the first action; do not reopen the choice solely by re-solving the visible case. Record order and record_id confer no authority."""
def second_prompt(task, first, condition):
    return RULES+'This is a continuation of your recorded provisional choice.\nFirst response: '+canonical(first)+'\nActive case: '+canonical(task['case'])+'\nEvidence records: '+canonical(records(task,condition))+'\n'+STANDING

def has_standing(r,c): return r['integrity']=='PASS' and all(r[k]==c[k] for k in ('case_id','contract','state_hash'))
def target(task,first,condition):
    return task['gold'] if condition=='current' or condition.startswith('conflict_') else first

def baseline(task,first,condition,kind):
    docs=records(task,condition)
    if kind=='preserve':return first
    if kind=='solve_case':return next(k for k,v in task['case']['candidates'].items() if v==solve(task['case']['state']))
    if kind=='old_shortcut':
        selected=[r for r in docs if r['record_id']=='evidence-1' and not r['case_id'].endswith('-other') and r['integrity']=='PASS' and r['recommendation'] is not None]
        return selected[0]['recommendation'] if selected else first
    def eligible(r):
        if kind in ('first_record','last_record'):return True
        ignored=kind[len('ignore_'):] if kind.startswith('ignore_') else None
        return all(f==ignored or (r[f]=='PASS' if f=='integrity' else r[f]==task['case'][f]) for f in FIELDS)
    recs=[r['recommendation'] for r in docs if r['recommendation'] is not None and eligible(r)]
    return (recs[0] if kind=='first_record' else recs[-1]) if recs else first
if __name__=='__main__':
    from pathlib import Path
    root=Path(__file__).resolve().parent
    for name,obj in [('tasks.json',make_cases()),('schema.json',SCHEMA)]:
        text=json.dumps(obj,indent=2)+'\n';p=root/name
        if p.exists():assert p.read_text()==text
        else:p.write_text(text)
    print('64 cases,',len(CONDITIONS),'conditions; 1024 calls/model.')
