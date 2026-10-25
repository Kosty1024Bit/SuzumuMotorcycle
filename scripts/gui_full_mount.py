import builtins, json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
p=builtins._suzumu_rider
world=u.EditorLevelLibrary.get_game_world()
item=u.GameItemSpawner.spawn_game_item(world,19871001)
item_bike=p.get_thrall_system_component().spawn_thrall_from_item(item,u.Transform(location=u.Vector(2000,1000,500)))
builtins._suzumu_bike=item_bike
p.set_actor_location(u.Vector(1840,1000,500),False,True)
p.mount(item_bike)
mi=p.get_mount_input(); builtins._suzumu_mount_input=mi
report={'mount':str(p.get_mount()),'bike':str(item_bike),'mounted':p.get_mount()==item_bike,'transition':p.get_is_in_mount_transition(),'target_values':{n:mi.get_target_speed_value(getattr(u.MountTargetSpeed,n)) for n in dir(u.MountTargetSpeed) if n.isupper() and n in ['WALKING_SPEED','RUNNING_SPEED','SPRINTING_SPEED','STATIONARY']}}
(ROOT/'evidence/PIE_full_mount.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] FULL MOUNT '+str(report))
