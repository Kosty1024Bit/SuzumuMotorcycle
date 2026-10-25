import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
bp=u.load_asset('/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
bike=actors.spawn_actor_from_class(bp.generated_class(),u.Vector(0,300,100),u.Rotator(),False)
bike.set_character_spawn_table_id('SuzumuMotorcycle')
report={'spawn_table':str(bike.source_spawn_table),'embedded_saddle':str(bike.get_embedded_saddle_id()),'mountable':bike.is_mountable(),'height_to_saddle':bike.get_editor_property('HeightToSaddle')}
for n in ['DefaultHealth','DefaultStamina']:
    report[n]=bike.get_editor_property(n)
report['stats_before_beginplay']={name:bike.get_int_stat(getattr(u.CharIntStatID,name),u.StatModifierMode.FULL) for name in ['ITEM_CONTAINER_SIZE','ENDURANCE_MAX','ENDURANCE_CURRENT','STAMINA_MAX']}
(ROOT/'evidence/mount_init_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] MOUNT INIT '+str(report))
assert report['embedded_saddle']=='19871002'
assert report['mountable']
