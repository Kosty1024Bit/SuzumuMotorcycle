import builtins, json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
p=builtins._suzumu_rider; b=builtins._suzumu_bike
report={'stats':{n:p.get_int_stat(getattr(u.CharIntStatID,n),u.StatModifierMode.FULL) for n in ['HEALTH_CURRENT','HEALTH_MAX','STAMINA_CURRENT','STAMINA_MAX']},'mount':str(p.get_mount()),'controller':str(p.get_controller()),'state':str(p.get_character_state()),'substates':str(p.get_substate_list()),'bike_mounted':str(b.call_method('GetIsMounted')),'root_parent':str(p.root_component.get_attach_parent()),'input_speed':str(p.get_mount_input().get_current_speed()),'target_speed':str(p.get_mount_input().get_current_target_speed())}
(ROOT/'evidence/PIE_rider_state.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] RIDER STATE '+str(report))
