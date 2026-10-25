import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
BP=u.BlueprintEditorLibrary
path='/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle'
bp=u.load_asset(path)
assert bp
data={}
for func in ['GetFallDamageReduction','ModifyIncomingHealthDamage']:
    graph=BP.add_function_override(bp,func)
    if not graph: data[func]='cannot override'; continue
    ed=u.BlueprintGraphEditor.get_graph_editor(graph)
    data[func]=[{'name':n.get_name(),'class':n.get_class().get_name(),'title':str(n.get_node_title()),'pins':[{'name':str(p.get_pin_name()),'dir':str(p.get_pin_direction()),'value':p.get_pin_value(),'links':[(q.get_owning_node().get_name(),str(q.get_pin_name())) for q in p.list_connected_pins()]} for p in n.list_all_pins()]} for n in ed.list_all_nodes()]
data['props']={}
cdo=u.get_default_object(bp.generated_class())
for name in ['HeightToSaddle','DefaultHealth','DefaultStamina','ThrallFallDamageCap','FallDamageReduction_PteorPact']:
    data['props'][name]=str(cdo.get_editor_property(name))
BP.compile_blueprint(bp); u.EditorAssetLibrary.save_loaded_asset(bp)
(ROOT/'evidence/override_pins.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
u.log('[SUZUMU] OVERRIDE PROBE COMPLETE')
