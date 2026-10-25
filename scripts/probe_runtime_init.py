import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
bp=u.load_asset('/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle')
cdo=u.get_default_object(bp.generated_class())
report={}
for name in ['set_character_spawn_table_id','on_character_spawn_table_i_dset','get_int_stat','set_int_stat','is_mountable','get_embedded_saddle_id','get_stat_holder']:
    report[name]=str(getattr(cdo,name).__doc__)
report['spawn_classes']={n:[m for m in dir(getattr(u,n)) if 'spawn' in m.lower() or 'npc' in m.lower()] for n in dir(u) if n in ['ConanGameMode','NPCSpawnManager','SpawnManager','SpawnTableComponent','SpawnTableHelper','SpawnData','NPCAttributeSystem','StatHolder']}
player=u.load_asset('/Game/Characters/BasePlayerChar')
report['mount_attachments']=[]
for graph in u.BlueprintEditorLibrary.list_graphs(player):
    if 'mount' not in graph.get_name().lower(): continue
    ed=u.BlueprintGraphEditor.get_graph_editor(graph)
    for n in ed.list_all_nodes():
        if any(t in str(n.get_node_title()).lower() for t in ['attach','saddle','relative','socket']):
            report['mount_attachments'].append({'graph':graph.get_name(),'title':str(n.get_node_title()),'pins':[{'name':str(p.get_pin_name()),'value':p.get_pin_value(),'links':[(q.get_owning_node().get_name(),str(q.get_pin_name())) for q in p.list_connected_pins()]} for p in n.list_all_pins()]})
(ROOT/'evidence/runtime_init_api.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] RUNTIME INIT API COMPLETE')
