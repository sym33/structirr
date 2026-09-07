"""Post-collection integrity audit; no additional inferential analysis or calls."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    for line in (ROOT/'FROZEN_SHA256SUMS').read_text().splitlines():
        h,n=line.split(maxsplit=1)
        if n=='PROTOCOL.md':
            with zipfile.ZipFile(ROOT/'provenance/protocol_original.zip') as z:
                data=z.read('PROTOCOL.md')
        else:
            data=(ROOT/n).read_bytes()
        assert hashlib.sha256(data).hexdigest()==h,n
    summary=json.loads((ROOT/'analysis_summary.json').read_text())
    assert set(summary['models'])=={'qwen2.5:32b','llama3.3:70b','gpt-5.6-luna'}
    audit={'frozen_hashes':'pass','models':{}}
    for name,m in summary['models'].items():
        rows=[json.loads(l) for l in (ROOT/'results'/name/'observations.jsonl').read_text().splitlines()]
        assert len(rows)==1024 and not any(r['error'] or r['tool_events'] for r in rows)
        assert len({(r['case_id'],r['stage'],r.get('condition')) for r in rows})==1024
        first={r['case_id']:r for r in rows if r['stage']=='first'}
        assert len(first)==64
        for c,v in m['conditions'].items():
            rr=[r for r in rows if r.get('condition')==c];assert len(rr)==64
            wrong=[r for r in rr if first[r['case_id']]['response']['action']!=r['gold']]
            right=[r for r in rr if first[r['case_id']]['response']['action']==r['gold']]
            assert v['repair']['k']==sum(r['response']['action']==r['gold'] for r in wrong)
            assert v['preservation']['k']==sum(r['response']['action']==r['gold'] for r in right)
            for r in rr:assert r['first_response']==first[r['case_id']]['response']
        local=[r for r in rows if r['backend']=='ollama']
        event_types=set()
        for r in rows:
            assert r['model']==name and json.loads(r['raw'])==r['response']
            if r['backend']=='ollama':
                assert r['invocation']['prompt']==r['prompt'] and r['invocation']['model']==name
                assert r['trace']['prompt_eval_count']+r['trace']['eval_count']<r['invocation']['options']['num_ctx']
            else:
                assert r['invocation'][r['invocation'].index('--model')+1]==name
                assert r['trace']['returncode']==0
                for line in r['trace']['stdout'].splitlines():
                    try:event=json.loads(line)
                    except ValueError:continue
                    if event.get('item',{}).get('type'):event_types.add(event['item']['type'])
        audit['models'][name]={'calls':len(rows),'raw_counts_crosscheck':'pass','response_bindings':'pass','errors':0,'max_local_prompt_tokens':max((r['trace']['prompt_eval_count'] for r in local),default=None),'hosted_item_types':sorted(event_types)}
    (ROOT/'ARCHIVE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
