import builtins, json, time, traceback
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
player=builtins._suzumu_rider; bike=builtins._suzumu_bike
player.set_actor_location(bike.get_actor_location()+u.Vector(-160,0,0),False,True)
player.server_initiate_mount(bike)
start=time.monotonic(); state={'last':0.0}
def observe(delta):
    now=time.monotonic()
    if now-state['last']<.5: return
    state['last']=now
    report={'elapsed':now-start,'mount':str(player.get_mount()),'transition':player.get_is_in_mount_transition(),'player_location':str(player.get_actor_location()),'bike_location':str(bike.get_actor_location()),'can_mount':str(player.can_mount(bike))}
    if player.get_mount()==bike or now-start>10:
        mi=player.get_mount_input()
        report['input']=str(mi)
        if mi:
            report['input_api']={n:str(getattr(mi,n).__doc__) for n in dir(mi) if any(t in n.lower() for t in ['speed','input','sprint','forward','movement','steer','target']) and not n.startswith('_')}
            input_bp=u.load_asset('/Game/Systems/Mounts_v2/BP_MountInput')
            report['input_vars']=list(u.BlueprintEditorLibrary.list_member_variable_names(input_bp,True))
            builtins._suzumu_mount_input=mi
        report['mounted']=player.get_mount()==bike
        (ROOT/'evidence/PIE_mount.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        u.log('[SUZUMU] MOUNTED '+str(report['mounted']))
        u.unregister_slate_post_tick_callback(builtins._suzumu_mount_observer)
builtins._suzumu_mount_observer=u.register_slate_post_tick_callback(observe)
