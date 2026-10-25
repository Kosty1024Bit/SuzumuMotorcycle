import builtins, json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
p=builtins._suzumu_rider; b=builtins._suzumu_bike
data={}
for actor,name in [(p,'player'),(b,'bike')]:
    a=actor.mesh.get_anim_instance()
    data[name]={'state':str(actor.get_character_state()),'anim':str(a),'montage':str(a.get_current_active_montage()) if a else None,'mesh_tick':actor.mesh.is_component_tick_enabled(),'mesh_visible':actor.mesh.is_visible(),'tickmode':str(actor.mesh.get_editor_property('visibility_based_anim_tick_option'))}
    if a:
        montage=a.get_current_active_montage()
        if montage:data[name]['montage_position']=a.montage_get_position(montage)
for name in ['CurrentMount','IsMounted','MountingMontage','MountingNPC','StartMountingFromRight']:
    try:data[name]=str(p.get_editor_property(name))
    except Exception:pass
player_bp=u.load_asset('/Game/Characters/BasePlayerChar')
data['mount_graphs']={}
for g in u.BlueprintEditorLibrary.list_graphs(player_bp):
    if g.get_name() not in ['BPStartMountProcessClient','BPMountServer','BPPostMountServerClient']:continue
    ed=u.BlueprintGraphEditor.get_graph_editor(g)
    data['mount_graphs'][g.get_name()]=[{'name':n.get_name(),'title':str(n.get_node_title()),'pins':[{'name':str(q.get_pin_name()),'value':q.get_pin_value(),'links':[(r.get_owning_node().get_name(),str(r.get_pin_name())) for r in q.list_connected_pins()]} for q in n.list_all_pins()]} for n in ed.list_all_nodes()]
(ROOT/'evidence/PIE_mount_diagnostics.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
u.SystemLibrary.execute_console_command(p,'a.Budget.Enabled 0')
for actor in [p,b]:
    actor.mesh.set_component_tick_enabled(True)
    actor.mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
    actor.mesh.set_editor_property('enable_update_rate_optimizations',False)
u.log('[SUZUMU] MOUNT DIAGNOSTICS READY')
