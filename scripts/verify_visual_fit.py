"""Check only this visual fix: vertex orientation and attachment-bone displacement."""
import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
LOCAL='/Game/Mods/SuzumuMotorcycle'
BP=u.BlueprintEditorLibrary
bp=u.load_asset(LOCAL+'/BP_SuzumuMotorcycle')
abp=u.load_asset(LOCAL+'/ABP_SuzumuSeatOffset')
assert BP.compile_blueprint(bp) and BP.compile_blueprint(abp)
rig=u.get_default_object(bp.generated_class()).mesh.get_editor_property('skeletal_mesh_asset')
pose=u.AnimPoseExtensions.get_reference_pose(rig.get_editor_property('skeleton'))
adjusted=u.AnimPoseExtensions.evaluate_animation_blueprint_with_input_pose(pose,rig,abp)
report={'checks':[],'bone_displacement_cm':{}}
for name in ['b_attachrider','b_saddle','b_root','b_pelvis']:
    before=u.AnimPoseExtensions.get_bone_pose(pose,name,u.AnimPoseSpaces.WORLD).translation
    after=u.AnimPoseExtensions.get_bone_pose(adjusted,name,u.AnimPoseSpaces.WORLD).translation
    delta=after-before
    expected=u.Vector(0,-10,-110) if name=='b_attachrider' else u.Vector(0,0,0)
    assert (delta-expected).length()<.01,(name,str(delta))
    report['bone_displacement_cm'][name]=[delta.x,delta.y,delta.z]
report['checks'].append('Only the rider attachment bone moved; original horse pose preserved')
world=u.EditorLoadingAndSavingUtils.new_blank_map(False)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
bike=actors.spawn_actor_from_class(bp.generated_class(),u.Vector(0,0,96),u.Rotator(),False)
body=next(c for c in bike.get_components_by_class(u.StaticMeshComponent) if c.get_name().startswith('SuzumuBody'))
t=body.get_world_transform()
mesh=body.get_editor_property('static_mesh')
bounds={}
for i,slot in enumerate(mesh.get_editor_property('static_materials')):
    verts,*_=u.ProceduralMeshLibrary.get_section_from_static_mesh(mesh,0,i)
    points=[u.MathLibrary.transform_location(t,v) for v in verts]
    bounds[str(slot.material_slot_name)]={'min_z':min(p.z for p in points),'max_z':max(p.z for p in points)}
front=bounds['Modeltire_front_Material005']; rear=bounds['Modeltire_rear_Material002']; seat=bounds['Modelseat_Material010']
assert abs(rear['min_z'])<.1 and abs(front['min_z'])<1, bounds
assert seat['min_z']>front['max_z'],bounds
report['checks'].append('Both tyres at ground level; seat above both wheels')
report['body_transform']=str(t)
report['part_height_cm']=bounds
report['blueprints']={o.get_name():str(o.get_editor_property('status')) for o in [bp,abp]}
report['all_passed']=True
(ROOT/'evidence/visual_fix_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
import builtins
builtins._suzumu_visual_bike=bike
u.log('[SUZUMU] VISUAL FIX CHECKS PASS')
