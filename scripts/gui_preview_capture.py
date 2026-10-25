import builtins, json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
w=u.EditorLevelLibrary.get_game_world(); pc=u.GameplayStatics.get_player_controller(w,0); gm=u.GameplayStatics.get_game_mode(w)
b=builtins._suzumu_bike
target=b.get_actor_location()+u.Vector(0,0,-30)
camera_pos=target+u.Vector(260,-300,160)
old=gm.get_editor_property('default_pawn_class')
gm.set_editor_property('default_pawn_class',u.DefaultPawn)
cam=gm.spawn_default_pawn_at_transform(pc,u.Transform(location=camera_pos))
gm.set_editor_property('default_pawn_class',old)
pc.possess(cam)
pc.set_control_rotation(u.MathLibrary.find_look_at_rotation(camera_pos,target))
pc.set_view_target_with_blend(cam,0)
u.SystemLibrary.execute_console_command(w,'r.SetRes 1280x720w')
u.SystemLibrary.execute_console_command(w,'HighResShot 1280x720 filename='+str(ROOT/'evidence/motorcycle_preview.png').replace('\\','/'))
builtins._suzumu_preview_camera=cam
u.log('[SUZUMU] PREVIEW CAPTURE REQUESTED')
