import json, re
from pathlib import Path
import unreal as u
OUT=Path(__file__).resolve().parents[1]/'evidence'
bp=u.load_asset('/Game/Characters/NPCs/Hooved_Wild/Blueprints/BP_NPC_Mounts_Horse_Knight')
cdo=u.get_default_object(bp.generated_class())
data={}
names=u.BlueprintEditorLibrary.list_member_variable_names(bp,True)
for full in names:
    name=str(full).rsplit('.',1)[-1]
    if not re.search('fall|stamina|endurance|container|inventory|heighttosaddle|defaulthealth|NPC.*Template',name,re.I): continue
    try:
        value=cdo.get_editor_property(name)
        data[name]=value.export_text() if isinstance(value,u.StructBase) else str(value)
    except Exception as ex: data[name]={'error':str(ex)}
for method in ['get_endurance_data','get_stamina_data','get_int_stat']:
    try:
        val=getattr(cdo,method)() if method!='get_int_stat' else cdo.get_int_stat(u.CharIntStatID.ITEM_CONTAINER_SIZE)
        data[method]=str(val)
    except Exception as ex: data[method]={'error':str(ex)}
(OUT/'horse_targeted.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
u.log('[SUZUMU] TARGETED COMPLETE')
