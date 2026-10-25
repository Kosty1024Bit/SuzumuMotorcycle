import json
from pathlib import Path
import unreal as u
OUT=Path(__file__).resolve().parents[1]/'evidence'
BP=u.BlueprintEditorLibrary
bp=u.load_asset('/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle')
graph=BP.find_graph(bp,'ModifyIncomingHealthDamage')
ed=u.BlueprintGraphEditor.get_graph_editor(graph)
report={}
report['nodes']=[s for s in ed.list_available_nodes([]) if any(w in s.lower() for w in ['classischild','objectisa','getclass','selectint','selectfloat','multiply','select'])]
report['pins']={n.get_name():[{ 'name':str(p.get_pin_name()),'schema':p.get_pin_type_as_json_schema()} for p in n.list_all_pins()] for n in ed.list_all_nodes()}
report['subobjectdocs']={n:str(getattr(u.SubobjectDataBlueprintFunctionLibrary,n).__doc__) for n in ['get_object_for_blueprint','get_associated_object','get_object']}
report['component_docs']={n:str(getattr(u.PrimitiveComponent,n).__doc__) for n in ['set_render_in_main_pass','set_render_in_depth_pass','set_hidden_in_game']}
report['functions']={}
for path in ['/Script/Engine.KismetMathLibrary.Multiply_DoubleDouble','/Script/Engine.KismetMathLibrary:Multiply_DoubleDouble','/Script/Engine.PrimitiveComponent.SetRenderInMainPass','/Script/Engine.PrimitiveComponent:SetRenderInMainPass']:
    obj=u.load_object(None,path)
    report['functions'][path]=str(obj)
cdo=u.get_default_object(bp.generated_class())
report['native_mesh']={'path':cdo.mesh.get_path_name(),'outer':cdo.mesh.get_outer().get_path_name(),'cdo':cdo.get_path_name()}
(OUT/'behavior_api.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] BEHAVIOR API COMPLETE')
