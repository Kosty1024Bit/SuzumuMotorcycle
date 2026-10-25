import builtins, json, time
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
p=builtins._suzumu_control_player; horse=builtins._suzumu_control_horse
index=horse.get_equipment_inventory_native().add_item(builtins._suzumu_control_saddle,'SuzumuQA')
p.mount(horse)
start=time.monotonic()
def done(delta):
    if time.monotonic()-start<5:return
    report={'inventory_index':index,'mount':str(p.get_mount()),'mounted':p.get_mount()==horse,'transition':p.get_is_in_mount_transition(),'state':str(p.get_character_state()),'current_mount':str(p.get_editor_property('CurrentMount'))}
    (ROOT/'evidence/PIE_baseline_mount.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    u.unregister_slate_post_tick_callback(builtins._suzumu_baseline_observer)
    u.log('[SUZUMU] BASELINE HORSE MOUNT '+str(report))
builtins._suzumu_baseline_observer=u.register_slate_post_tick_callback(done)
