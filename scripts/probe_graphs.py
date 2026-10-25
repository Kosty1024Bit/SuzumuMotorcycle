import json
from pathlib import Path
import unreal as u
OUT=Path(__file__).resolve().parents[1]/'evidence'
BP=u.BlueprintEditorLibrary
def graph_dump(graph):
    ed=u.BlueprintGraphEditor.get_graph_editor(graph)
    result=[]
    for node in ed.list_all_nodes():
        pins=[]
        for pin in node.list_all_pins():
            pins.append({'name':str(pin.get_pin_name()),'direction':str(pin.get_pin_direction()),'value':pin.get_pin_value(),'type':str(pin.get_pin_type_display_string()),'links':[(p.get_owning_node().get_name(),str(p.get_pin_name())) for p in pin.list_connected_pins()]})
        result.append({'name':node.get_name(),'title':str(node.get_node_title()),'class':node.get_class().get_path_name(),'pins':pins})
    return result
targets={
    '/Game/Characters/BaseBPCombat':['GetFallDamageReduction','CalculateFallDamagePercent','ApplyFallDamage','ServerEndFalling'],
    '/Game/Characters/NPCs/Hooved_Wild/Blueprints/BP_NPC_Mounts_Horse':['FindSaddleData','UserConstructionScript'],
    '/Game/Characters/BaseNPC':['InitializeCombatStats','UserConstructionScript'],
}
for path,names in targets.items():
    bp=u.load_asset(path)
    (OUT/(bp.get_name()+'.variables.json')).write_text(json.dumps(list(BP.list_member_variable_names(bp,True)),indent=2),encoding='utf-8')
    data={g.get_name():graph_dump(g) for g in BP.list_graphs(bp) if g.get_name() in names}
    (OUT/(bp.get_name()+'.graphs.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
controller=u.load_class(None,'/Script/DreamworldMods.ModController')
(OUT/'modcontroller_doc.txt').write_text(str(controller)+'\n'+str(type(u.get_default_object(controller)).__doc__),encoding='utf-8')
# Child assets reference game code, preserving horse behavior without copying its graphs.
folder='/Game/Mods/SuzumuMotorcycle'
for name,parent in [('BP_SuzumuMotorcycle',u.EditorAssetLibrary.load_blueprint_class('/Game/Characters/NPCs/Hooved_Wild/Blueprints/BP_NPC_Mounts_Horse_Knight')),('BP_SuzumuModController',controller)]:
    path=folder+'/'+name
    bp=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else BP.create_blueprint_asset_with_parent(path,parent)
    assert bp, 'Could not create '+path
    BP.compile_blueprint(bp)
    assert u.EditorAssetLibrary.save_loaded_asset(bp)
    report={'vars':list(BP.list_member_variable_names(bp,True)), 'functions':[str(x) for x in BP.list_functions(bp)], 'graphs':[g.get_name() for g in BP.list_graphs(bp)]}
    if name=='BP_SuzumuModController':
        graph=BP.add_function_override(bp,'ModDataTableOperations')
        if graph:
            ed=u.BlueprintGraphEditor.get_graph_editor(graph)
            report['operations']=graph_dump(graph)
            report['nodes']=list(ed.list_available_nodes([]))
        BP.compile_blueprint(bp); u.EditorAssetLibrary.save_loaded_asset(bp)
    (OUT/(name+'.created.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    u.log('[SUZUMU] CREATED '+path)
