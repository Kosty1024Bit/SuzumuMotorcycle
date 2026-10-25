"""Local file job queue for the official Dev Kit Python commandlet.

Jobs execute only scripts from this mod's scripts directory. No network listener.
Place a numbered JSON job in evidence/queue with a script name; results are journaled.
The worker exits on evidence/worker.stop or after 45 minutes.
"""
import json, runpy, time, traceback
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/'evidence/queue'; QUEUE.mkdir(exist_ok=True)
(ROOT/'evidence/worker.ready').write_text('ready',encoding='utf-8')
u.log('[SUZUMU] WORKER READY')
deadline=time.monotonic()+2700
while time.monotonic()<deadline and not (ROOT/'evidence/worker.stop').exists():
    for jobfile in sorted(QUEUE.glob('*.json')):
        done=jobfile.with_suffix('.result')
        if done.exists(): continue
        try:
            job=json.loads(jobfile.read_text(encoding='utf-8'))
            script=(ROOT/'scripts'/job['script']).resolve()
            assert script.parent==ROOT/'scripts', 'Script must be in mod scripts directory'
            u.log('[SUZUMU] JOB '+jobfile.name+' '+script.name)
            runpy.run_path(str(script),run_name='__main__')
            result={'ok':True,'script':script.name}
        except BaseException:
            result={'ok':False,'error':traceback.format_exc()}
            u.log_error('[SUZUMU] '+result['error'])
        done.write_text(json.dumps(result,indent=2),encoding='utf-8')
    time.sleep(0.25)
u.log('[SUZUMU] WORKER EXIT')
