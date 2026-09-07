import os,signal,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
try:
    for model in ('qwen2.5:32b','llama3.3:70b'):
        subprocess.run([sys.executable,str(root/'run.py'),'--model',model,'--backend','ollama'],cwd=root,check=True)
finally:
    pid=int(sys.argv[1])
    cmd=Path(f'/proc/{pid}/cmdline').read_bytes() if Path(f'/proc/{pid}/cmdline').exists() else b''
    if b'/home/ki-admin/ollama_local/bin/ollama\x00serve' in cmd:os.kill(pid,signal.SIGTERM)
