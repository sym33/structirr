"""Launch the specified V5 jobs; do not stop or reconfigure other workloads."""
import hashlib,json,os,socket,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
for line in (ROOT/'FROZEN_SHA256SUMS').read_text().splitlines():
    h,n=line.split(maxsplit=1);assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
with socket.socket() as s:assert s.connect_ex(('127.0.0.1',11435))!=0,'Dedicated port already occupied'
env=dict(os.environ,CUDA_VISIBLE_DEVICES='1',OLLAMA_HOST='127.0.0.1:11435',OLLAMA_MODELS='/home/ki-admin/ollama_models',OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1')
with (ROOT/'dedicated_ollama.log').open('w') as log:
    service=subprocess.Popen(['/home/ki-admin/ollama_local/bin/ollama','serve'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
(ROOT/'dedicated_ollama.pid').write_text(str(service.pid))
for attempt in range(40):
    try:
        with urllib.request.urlopen('http://127.0.0.1:11435/api/tags',timeout=2) as r:inventory=json.load(r)
        break
    except Exception:time.sleep(.5)
else:raise RuntimeError('Dedicated service failed to start')
(ROOT/'model_inventory.json').write_text(json.dumps(inventory,indent=2))
for name,cmd in [('ollama_version.txt',['/home/ki-admin/ollama_local/bin/ollama','--version']),('codex_version.txt',['/home/ki-admin/codex_cli/node_modules/.bin/codex','--version'])]:
    (ROOT/name).write_text(subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT))
for name,cmd in [('luna',[sys.executable,'run.py','--model','gpt-5.6-luna','--backend','codex','--workers','4']),('local_models',[sys.executable,'run_local.py',str(service.pid)])]:
    with (ROOT/(name+'.log')).open('w') as log:
        proc=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    (ROOT/(name+'.pid')).write_text(str(proc.pid))
    print(name,proc.pid)
