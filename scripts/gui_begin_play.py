import builtins, json, traceback, time
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
world=u.EditorLoadingAndSavingUtils.load_map('/Game/Dev/AlmostEmpty')
assert world
editor=u.get_editor_subsystem(u.EditorActorSubsystem)
builtins._suzumu_editor_world=world
# Place a test mount before PIE. Its real BeginPlay will read its spawn template.
bp=u.load_asset('/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle')
actor=editor.spawn_actor_from_class(bp.generated_class(),u.Vector(0,0,250),u.Rotator(),False)
actor.set_actor_label('Suzumu_RuntimeTest')
actor.set_character_spawn_table_id('SuzumuMotorcycle')
actor.set_editor_property('IsThrall',True)
builtins._suzumu_begin_time=time.monotonic()
settings_class=u.load_class(None,'/Script/UnrealEd.LevelEditorPlaySettings')
if settings_class:
    settings=u.get_default_object(settings_class)
    settings.set_editor_property('GameGetsMouseControl',False)
    settings.set_editor_property('PlayNumberOfClients',1)
    # This kit omits the enum wrapper. Its current stored value was confirmed as 0
    # (PIE_Standalone); do not try to round-trip the unwrapped enum through Python.
u.get_editor_subsystem(u.LevelEditorSubsystem).editor_request_begin_play()
u.log('[SUZUMU] PIE REQUESTED')
