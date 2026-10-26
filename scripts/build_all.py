import runpy
from pathlib import Path
import unreal as u
SCRIPTS=Path(__file__).resolve().parent
for name in ['probe_graphs.py','import_model.py','author_tables.py','author_seat_pose.py','author_behavior.py','verify_editor.py']:
    u.log('[SUZUMU] BUILD STAGE '+name)
    runpy.run_path(str(SCRIPTS/name),run_name='__main__')
u.log('[SUZUMU] AUTHORING COMPLETE')
