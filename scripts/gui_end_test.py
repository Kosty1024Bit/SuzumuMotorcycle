import builtins
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
sub=u.get_editor_subsystem(u.LevelEditorSubsystem)
sub.editor_request_end_play()
def finish(delta):
    if sub.is_in_play_in_editor():return
    u.unregister_slate_post_tick_callback(builtins._suzumu_end_handle)
    u.EditorLoadingAndSavingUtils.new_blank_map(False)
    (ROOT/'evidence/gui.stop').write_text('End local runtime test.',encoding='utf-8')
builtins._suzumu_end_handle=u.register_slate_post_tick_callback(finish)
