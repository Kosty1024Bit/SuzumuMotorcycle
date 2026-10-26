import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
BP=u.BlueprintEditorLibrary
abp=u.load_asset('/Game/Mods/SuzumuMotorcycle/ABP_SuzumuSeatOffset')
g=BP.find_graph(abp,'AnimGraph'); ed=u.BlueprintGraphEditor.get_graph_editor(g)
root=next(n for n in ed.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_Root')
ed.remove_nodes([n for n in ed.list_all_nodes() if n!=root])
created={}
for key,path in [('input','Animation|LinkedAnimGraphs|InputPose'),('to_component','Animation|ConvertSpaces|LocalToComponent'),('offset','Animation|SkeletalControls|Transform(Modify)Bone'),('to_local','Animation|ConvertSpaces|ComponentToLocal')]:
    n=ed.create_node_from_name(path,u.Vector2D(0,0),[]); assert n,path
    created[key]=n
report={'nodes':{},'classes':{}}
for key,n in created.items():
    report['nodes'][key]={'class':n.get_class().get_name(),'pins':[{'name':str(p.get_pin_name()),'direction':str(p.get_pin_direction()),'value':p.get_pin_value()} for p in n.list_all_pins()]}
    try:report['nodes'][key]['node']=n.get_editor_property('node').export_text()
    except Exception as ex:report['nodes'][key]['node']=str(ex)
for name in dir(u):
    if any(s in name.lower() for s in ['animposeext','animationlibrary','animationblueprintlib']):
        cls=getattr(u,name)
        report['classes'][name]={n:str(getattr(cls,n).__doc__) for n in dir(cls) if any(t in n.lower() for t in ['pose','bone'])}
report['anim_component_methods']={n:str(getattr(u.SkeletalMeshComponent,n).__doc__) for n in dir(u.SkeletalMeshComponent) if any(k in n.lower() for k in ['animation','position','bone_transform'])}
bp=u.load_asset('/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle')
cs=BP.find_graph(bp,'UserConstructionScript'); ce=u.BlueprintGraphEditor.get_graph_editor(cs)
n=ce.add_call_function_node('/Script/Engine.SkeletalMeshComponent:SetOverridePostProcessAnimBP')
report['override_pins']=[str(p.get_pin_name()) for p in n.list_all_pins()]
ce.remove_nodes([n])
u.EditorAssetLibrary.save_loaded_asset(abp)
(ROOT/'evidence/seat_graph_stage2.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] SEAT GRAPH NODES CREATED')
