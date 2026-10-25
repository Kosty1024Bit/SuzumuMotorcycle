import builtins
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
w=u.EditorLevelLibrary.get_game_world(); b=builtins._suzumu_bike
for actor in u.GameplayStatics.get_all_actors_of_class(w,u.ConanCharacter):
    if actor!=b: actor.set_actor_hidden_in_game(True)
body=next(c for c in b.get_components_by_class(u.StaticMeshComponent) if c.get_name().startswith('SuzumuBody'))
# Transient visual equivalent of replacing the incorrect import pitch with yaw.
body.set_relative_rotation(u.Rotator(pitch=0,yaw=0,roll=180),False,True)
body.set_relative_location(u.Vector(0,0,27.398354),False,True)
u.SystemLibrary.execute_console_command(w,'HighResShot 1280x720 filename='+str(ROOT/'evidence/motorcycle_upright.png').replace('\\','/'))
u.log('[SUZUMU] UPRIGHT PREVIEW REQUESTED')
