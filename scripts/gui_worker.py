"""Run short Dev Kit verification jobs between editor frames without mouse/keyboard input."""
import builtins, json, runpy, traceback
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/'evidence/gui_queue'; QUEUE.mkdir(exist_ok=True)
STATE={'busy':False}
def tick(delta):
    if STATE['busy']: return
    if (ROOT/'evidence/gui.stop').exists():
        u.unregister_slate_post_tick_callback(builtins._suzumu_tick_handle)
        u.SystemLibrary.quit_editor()
        return
    for jobfile in sorted(QUEUE.glob('*.json')):
        resultfile=jobfile.with_suffix('.result')
        if resultfile.exists(): continue
        STATE['busy']=True
        try:
            job=json.loads(jobfile.read_text(encoding='utf-8'))
            script=(ROOT/'scripts'/job['script']).resolve()
            assert script.parent==ROOT/'scripts'
            runpy.run_path(str(script),run_name='__main__')
            result={'ok':True}
        except BaseException:
            result={'ok':False,'error':traceback.format_exc()}
            u.log_error('[SUZUMU] '+result['error'])
        finally:
            STATE['busy']=False
        resultfile.write_text(json.dumps(result,indent=2),encoding='utf-8')
        break
builtins._suzumu_tick_handle=u.register_slate_post_tick_callback(tick)
(ROOT/'evidence/gui.ready').write_text('ready',encoding='utf-8')
u.log('[SUZUMU] GUI WORKER READY')
