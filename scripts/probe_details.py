import json, re, inspect
from pathlib import Path
import unreal as u
OUT=Path(__file__).resolve().parents[1]/'evidence'
BP=u.BlueprintEditorLibrary
def log(s): u.log('[SUZUMU] '+str(s))
for path in ['/Game/Systems/SpawnTable/ProfessionTemplateDataTable','/Game/Systems/Survival/Gathering/Gathering_v2/ItemNameToTemplateID']:
    dt=u.load_asset(path)
    (OUT/(path.rsplit('/',1)[-1]+'.csv')).write_text(u.DataTableFunctionLibrary.export_data_table_to_csv_string(dt),encoding='utf-8')
    log('TABLE '+path)
def desc(obj):
    result={}
    names=set(dir(obj))
    if isinstance(obj,u.Actor):
        bp=BP.get_blueprint_for_class(obj.get_class())
        if isinstance(bp,tuple): bp=next((x for x in bp if isinstance(x,u.Blueprint)),None)
        if bp: names.update(str(n).rsplit(':',1)[-1] for n in BP.list_member_variable_names(bp,True))
    for k in sorted(names):
        if k.startswith('_'): continue
        try:
            val=obj.get_editor_property(k)
            result[k]=str(val)[:5000]
        except Exception: pass
    return result
report={}
for path in ['/Game/Characters/NPCs/Hooved_Wild/Blueprints/BP_NPC_Mounts_Horse_Knight','/Game/Characters/NPCs/Hooved_Wild/Blueprints/BP_NPC_Mounts_Horse','/Game/Characters/BaseNPC','/Game/Characters/BaseBPCombat','/Game/Characters/BasePlayerChar']:
    bp=u.load_asset(path); cdo=u.get_default_object(bp.generated_class())
    data={'defaults':desc(cdo),'functions':[], 'events':[], 'graphs':[],'components':{}}
    for typ in ['functions','events']:
        data[typ]=[str(x) for x in getattr(BP,'list_'+typ)(bp)]
    data['graphs']=[g.get_name() for g in BP.list_graphs(bp)]
    sds=u.get_engine_subsystem(u.SubobjectDataSubsystem)
    for handle in sds.k2_gather_subobject_data_for_blueprint(bp):
        sd=u.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
        ob=u.SubobjectDataBlueprintFunctionLibrary.get_associated_object(sd)
        if ob and isinstance(ob,u.ActorComponent):
            data['components'][ob.get_name()]={'class':ob.get_class().get_path_name(),'properties':desc(ob)}
    (OUT/(path.rsplit('/',1)[-1]+'.details.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
    log('DETAILS '+path)
docs={}
for cls in ['BlueprintGraphEditor','BlueprintGraphPin','BlueprintEditorLibrary','EdGraphNode','SubobjectDataSubsystem','CharFloatStatID','CharIntStatID','EnduranceData','StaminaData','ModController','DataTableFactory','FbxImportUI']:
    c=getattr(u,cls,None)
    if c:
        docs[cls]={n:str(getattr(c,n).__doc__) for n in dir(c) if not n.startswith('_')}
(OUT/'api_docs.json').write_text(json.dumps(docs,indent=2),encoding='utf-8')
(OUT/'stat_types.json').write_text(json.dumps([n for n in dir(u) if any(s in n.lower() for s in ['stat','endurance','modcontroller','exportert3d'])],indent=2),encoding='utf-8')
enums={}
for name in dir(u):
    if ('stat' in name.lower() or 'endurance' in name.lower()) and isinstance(getattr(u,name),type):
        c=getattr(u,name)
        if issubclass(c,u.EnumBase):
            enums[name]={n:str(getattr(c,n)) for n in dir(c) if n.isupper()}
(OUT/'stat_enums.json').write_text(json.dumps(enums,indent=2),encoding='utf-8')
log('DETAILS COMPLETE')
