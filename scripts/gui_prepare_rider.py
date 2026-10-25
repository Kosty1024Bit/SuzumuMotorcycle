import builtins, json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
player=builtins._suzumu_rider
report={'old_anim':str(player.mesh.get_editor_property('anim_class'))}
player.mesh.set_anim_instance_class(u.load_class(None,'/Game/Master_AnimBP/AB_human_male.AB_human_male_C'))
player.mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
report['new_anim']=str(player.mesh.get_editor_property('anim_class'))
report['mesh']=str(player.mesh.get_editor_property('skeletal_mesh_asset'))
(ROOT/'evidence/PIE_rider.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] TEST RIDER ANIMATION READY')
