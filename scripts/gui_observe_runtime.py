import builtins, json, time, traceback
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
start=time.monotonic()
state={'last':0.0}
def observe(delta):
    now=time.monotonic()
    if now-state['last']<1: return
    state['last']=now
    report={'elapsed':now-start}
    try:
        world=u.EditorLevelLibrary.get_game_world()
        report['world']=world.get_name() if world else None
        if world:
            gs=u.GameplayStatics.get_game_state(world)
            report['game_state']=gs.get_class().get_path_name() if gs else None
            cls=u.load_class(None,'/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle.BP_SuzumuMotorcycle_C')
            actors=u.GameplayStatics.get_all_actors_of_class(world,cls)
            report['count']=len(actors)
            if actors:
                bike=actors[0]
                report['actor']=bike.get_path_name(); report['location']=str(bike.get_actor_location())
                report['spawn']=str(bike.source_spawn_table)
                report['saddle']=str(bike.get_embedded_saddle_id())
                report['mountable']=bike.is_mountable()
                report['is_thrall']=bike.get_editor_property('IsThrall')
                report['stats']={name:bike.get_int_stat(getattr(u.CharIntStatID,name),u.StatModifierMode.FULL) for name in ['ITEM_CONTAINER_SIZE','ENDURANCE_MAX','ENDURANCE_CURRENT','STAMINA_MAX','HEALTH_MAX','ATTRIBUTE_MIGHT','ATTRIBUTE_ATHLETICISM','ATTRIBUTE_HEALTH','ATTRIBUTE_STAMINA']}
                report['thrall_component']=str(bike.get_thrall_component())
                pawn=u.GameplayStatics.get_player_pawn(world,0)
                report['player']=pawn.get_path_name() if pawn else None
        (ROOT/'evidence/PIE_observation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        if now-start>15 or (report.get('stats',{}).get('ENDURANCE_MAX')==1600 and report.get('saddle')=='19871002'):
            u.unregister_slate_post_tick_callback(builtins._suzumu_observe_handle)
            (ROOT/'evidence/PIE_observation.done').write_text('done',encoding='utf-8')
            u.log('[SUZUMU] PIE OBSERVATION '+str(report))
    except Exception:
        report['error']=traceback.format_exc()
        (ROOT/'evidence/PIE_observation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        u.unregister_slate_post_tick_callback(builtins._suzumu_observe_handle)
builtins._suzumu_observe_handle=u.register_slate_post_tick_callback(observe)
