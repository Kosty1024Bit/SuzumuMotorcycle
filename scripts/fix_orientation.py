import runpy
from pathlib import Path
import unreal as u
# FBX reimport options did not replace the cached Interchange vertex transform.
# Keep the shipped source mesh and correct the actual component plus rider socket.
for name in ['author_seat_pose.py','author_behavior.py','verify_visual_fit.py']:
    runpy.run_path(str(Path(__file__).parent/name),run_name='__main__')
u.log('[SUZUMU] COMPONENT ORIENTATION AND RIDER SOCKET FIX VERIFIED')
