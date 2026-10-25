import runpy
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
flag=ROOT/'evidence/force_reimport'
flag.write_text('Reimport with explicit yaw, pitch and roll keywords.',encoding='utf-8')
try:
    runpy.run_path(str(Path(__file__).parent/'import_model.py'),run_name='__main__')
finally:
    flag.unlink(missing_ok=True)
runpy.run_path(str(Path(__file__).parent/'verify_editor.py'),run_name='__main__')
u.log('[SUZUMU] FINAL ORIENTATION FIX VERIFIED')
