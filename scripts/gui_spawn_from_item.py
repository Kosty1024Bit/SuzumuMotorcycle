import builtins, json, traceback
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
report={}
try:
    world=u.EditorLevelLibrary.get_game_world(); assert world
    gm=u.GameplayStatics.get_game_mode(world)
    pc=u.GameplayStatics.get_player_controller(world,0)
    report['game_mode']=str(gm); report['default_pawn_class']=str(gm.get_editor_property('default_pawn_class'))
    player=u.GameplayStatics.get_player_pawn(world,0)
    if not isinstance(player,u.ConanCharacter):
        # The Dev Kit's empty map starts with a spectator and no default pawn.
        # Supply a test pawn class only on this transient PIE game-mode instance.
        original_pawn_class=gm.get_editor_property('default_pawn_class')
        gm.set_editor_property('default_pawn_class',u.load_class(None,'/Game/Characters/BasePlayerChar.BasePlayerChar_C'))
        player=gm.spawn_default_pawn_at_transform(pc,u.Transform(location=u.Vector(1000,1000,500)))
        gm.set_editor_property('default_pawn_class',original_pawn_class)
        report['spawned_player']=str(player)
        assert isinstance(player,u.ConanCharacter),report['spawned_player']
        pc.possess(player)
    report['player']=player.get_path_name()
    component=player.get_thrall_system_component(); report['thrall_system']=str(component)
    assert component
    item=u.GameItemSpawner.spawn_game_item(world,19871001)
    report['item']=str(item); assert isinstance(item,u.ThrallItem)
    report['item_actor_class']=str(item.get_thrall_actor_class())
    bike=component.spawn_thrall_from_item(item,u.Transform(location=u.Vector(1250,1000,500)))
    report['bike']=str(bike); assert bike
    builtins._suzumu_rider=player; builtins._suzumu_bike=bike
    report['saddle']=str(bike.get_embedded_saddle_id())
    report['thrall_component']=str(bike.get_thrall_component())
    report['stats']={name:bike.get_int_stat(getattr(u.CharIntStatID,name),u.StatModifierMode.FULL) for name in ['ITEM_CONTAINER_SIZE','ENDURANCE_MAX','ENDURANCE_CURRENT','STAMINA_MAX','HEALTH_MAX','ATTRIBUTE_MIGHT','ATTRIBUTE_ATHLETICISM','ATTRIBUTE_HEALTH','ATTRIBUTE_STAMINA']}
    report['can_mount']=str(player.can_mount(bike))
except BaseException:
    report['error']=traceback.format_exc()
(ROOT/'evidence/PIE_item_spawn.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] ITEM SPAWN '+str(report))
