import builtins, json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
b=builtins._suzumu_bike
body=next(c for c in b.get_components_by_class(u.StaticMeshComponent) if c.get_name().startswith('SuzumuBody'))
mesh=body.get_editor_property('static_mesh')
data={'actor_rotation':str(b.get_actor_rotation()),'body_rotation':str(body.get_relative_transform()),'rotator_test':str(u.Rotator(0,180,0)),'import_rotation':str(mesh.get_editor_property('asset_import_data').get_editor_property('import_rotation')),'health':{n:b.get_int_stat(getattr(u.CharIntStatID,n),u.StatModifierMode.FULL) for n in ['HEALTH_CURRENT','HEALTH_MAX']}}
(ROOT/'evidence/orientation_check.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
u.log('[SUZUMU] ORIENTATION CHECK '+str(data))
