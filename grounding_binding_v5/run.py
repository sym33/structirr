"""Resumable paired evaluation. One frozen model-generated first response per case.
No response-based retries; error observations are retained. Synthetic inputs only.
"""
import argparse, concurrent.futures, datetime, hashlib, json, os, random, subprocess, threading, time, urllib.request
from pathlib import Path
from design import CONDITIONS, SCHEMA, SEED, canonical, digest, first_prompt, second_prompt
ROOT=Path(__file__).resolve().parent
CODEX='/home/ki-admin/codex_cli/node_modules/.bin/codex'
LOCK=threading.Lock()
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def command(model,output):
    return [CODEX,'exec','--ephemeral','--skip-git-repo-check','--ignore-user-config','--sandbox','read-only','--model',model,'--color','never','--json','--output-schema',str(ROOT/'schema.json'),'-o',str(output),'-c','model_reasoning_effort="low"','-c','features.shell_tool=false','-c','features.unified_exec=false','-c','web_search="disabled"','-c','features.apps=false','-c','features.plugins=false','--','-']
def call(model,backend,prompt,stem):
    started=utc(); clock=time.monotonic(); raw=''; error=None; parsed=None; trace=None; invocation=None; tools=[]
    try:
        if backend=='ollama':
            body={'model':model,'prompt':prompt,'stream':False,'format':SCHEMA,'options':{'temperature':0,'num_ctx':8192,'num_predict':128,'seed':SEED},'keep_alive':'5m'}
            invocation=body
            req=urllib.request.Request(os.environ.get('EVAL_OLLAMA_URL','http://127.0.0.1:11435')+'/api/generate',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=600) as r: trace=json.load(r)
            raw=trace['response']
        else:
            output=ROOT/'results'/model/(stem+'.answer.txt'); output.parent.mkdir(parents=True,exist_ok=True)
            invocation=command(model,output)
            proc=subprocess.run(invocation,input=prompt,text=True,capture_output=True,timeout=240,cwd=ROOT/'runtime')
            trace={'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
            for line in proc.stdout.splitlines():
                try: event=json.loads(line)
                except ValueError: continue
                item=event.get('item',{})
                if item.get('type') in ('command_execution','mcp_tool_call','web_search','tool_call'): tools.append(item)
            raw=output.read_text() if output.exists() else ''
            if proc.returncode: raise RuntimeError('CLI exit '+str(proc.returncode))
            if tools: raise RuntimeError('Unexpected tool use')
        parsed=json.loads(raw)
        if set(parsed)!={'action'} or parsed['action'] not in ('A','B'): raise ValueError('Invalid action schema')
    except Exception as e: error=repr(e)
    return {'started_utc':started,'elapsed_s':time.monotonic()-clock,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'raw':raw,'response':parsed,'error':error,'backend':backend,'model':model,'invocation':invocation,'trace':trace,'tool_events':tools}
def append(path,row):
    with LOCK:
        with path.open('a') as f: f.write(json.dumps(row,ensure_ascii=True)+'\n'); f.flush(); os.fsync(f.fileno())
def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--backend',choices=['ollama','codex'],required=True);p.add_argument('--workers',type=int,default=1);p.add_argument('--smoke',action='store_true');args=p.parse_args()
    (ROOT/'runtime').mkdir(exist_ok=True);(ROOT/'results'/args.model).mkdir(parents=True,exist_ok=True)
    if args.smoke:
        row=call(args.model,args.backend,'Return exactly this JSON object and do not use tools: {"action":"A"}','smoke')
        (ROOT/'results'/args.model/'smoke.json').write_text(json.dumps(row,indent=2))
        print(json.dumps({'model':args.model,'response':row['response'],'error':row['error'],'elapsed':row['elapsed_s']}),flush=True)
        raise SystemExit(bool(row['error']))
    tasks=json.loads((ROOT/'tasks.json').read_text()); path=ROOT/'results'/args.model/'observations.jsonl'
    old=[json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []
    done={(r['case_id'],r['stage'],r.get('condition')):r for r in old}
    if len(done)!=len(old): raise RuntimeError('Duplicate observations')
    status=ROOT/'results'/args.model/'status.json'
    status.write_text(json.dumps({'state':'running','started':utc(),'pid':os.getpid(),'model':args.model,'planned_calls':len(tasks)*(1+len(CONDITIONS))}))
    def episode(t):
        cid=t['case']['case_id']; key=(cid,'first',None)
        first=done.get(key)
        if first is None:
            first={'case_id':cid,'stage':'first','gold':t['gold'],'family':t['case']['state']['family'],**call(args.model,args.backend,first_prompt(t),cid+'-first')}
            append(path,first)
        if first['error']:
            print(json.dumps({'case_id':cid,'first_error':first['error']}),flush=True);return
        order=list(CONDITIONS);random.Random(SEED+int(cid.split('-')[1])*100+int(cid.split('-')[2])).shuffle(order)
        for condition in order:
            if (cid,'second',condition) in done: continue
            row={'case_id':cid,'stage':'second','condition':condition,'gold':t['gold'],'family':t['case']['state']['family'],'first_response':first['response'],'first_response_sha256':digest(first['response']),**call(args.model,args.backend,second_prompt(t,first['response'],condition),cid+'-'+condition)}
            append(path,row)
            if row['error']: print(json.dumps({'case_id':cid,'condition':condition,'error':row['error']}),flush=True)
        print(json.dumps({'completed_case':cid,'model':args.model,'time':utc()}),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(episode,tasks))
    rows=[json.loads(l) for l in path.read_text().splitlines()]
    status.write_text(json.dumps({'state':'complete' if len(rows)==len(tasks)*(1+len(CONDITIONS)) and not any(r['error'] for r in rows) else 'complete_with_errors','finished':utc(),'records':len(rows),'errors':sum(bool(r['error']) for r in rows)}))
if __name__=='__main__': main()
