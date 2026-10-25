import builtins, json, time
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
w=u.EditorLevelLibrary.get_game_world(); gm=u.GameplayStatics.get_game_mode(w); pc=u.GameplayStatics.get_player_controller(w,0)
old=gm.get_editor_property('default_pawn_class')
gm.set_editor_property('default_pawn_class',u.load_class(None,'/Game/Characters/BasePlayerChar.BasePlayerChar_C'))
p=gm.spawn_default_pawn_at_transform(pc,u.Transform(location=u.Vector(3000,1000,500))); gm.set_editor_property('default_pawn_class',old)
pc.possess(p)
p.mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
item=u.GameItemSpawner.spawn_game_item(w,92229)
horse=p.get_thrall_system_component().spawn_thrall_from_item(item,u.Transform(location=u.Vector(3160,1000,500)))
# The ordinary horse needs a saddle; supply the same game-native embedded saddle route for this control.
data={'horse':str(horse),'saddle':str(horse.get_embedded_saddle_id()),'player':str(p)}
equipment=horse.get_equipment_inventory_native()
saddle=u.GameItemSpawner.spawn_game_item(w,2706)
data['inventory_api']={n:str(getattr(equipment,n).__doc__) for n in dir(equipment) if n in ['add_item','add_item_at','insert_item','add_to_inventory']}
(ROOT/'evidence/PIE_baseline_setup.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
builtins._suzumu_control_player=p; builtins._suzumu_control_horse=horse; builtins._suzumu_control_saddle=saddle
u.log('[SUZUMU] HORSE CONTROL CREATED')
