"""Inspect geometry and the mount attachment API, without playing or editing game saves."""
import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
bp=u.load_asset('/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle')
cdo=u.get_default_object(bp.generated_class())
mesh=u.load_asset('/Game/Mods/SuzumuMotorcycle/Art/SM_SuzumuMotorcycle')
report={'mesh_bounds':str(mesh.get_bounds()),'import_data':{},'api':{},'parts':[]}
report['mesh_component_api']={n:str(getattr(cdo.mesh,n).__doc__) for n in dir(cdo.mesh) if any(k in n.lower() for k in ['post_process','socket','skeletal_mesh','relative_location'])}
data=mesh.get_editor_property('asset_import_data')
for name in ['import_rotation','import_translation','import_uniform_scale','convert_scene','transform_vertex_to_absolute','bake_pivot_in_vertex']:
    try:report['import_data'][name]=str(data.get_editor_property(name))
    except Exception as ex:report['import_data'][name]=str(ex)
for name in dir(cdo):
    if any(s in name.lower() for s in ['mount','saddle','rider','socket']):
        member=getattr(cdo,name)
        report['api'][name]=str(member.__doc__) if callable(member) else str(member)
world=u.EditorLoadingAndSavingUtils.new_blank_map(False)
bike=u.get_editor_subsystem(u.EditorActorSubsystem).spawn_actor_from_class(bp.generated_class(),u.Vector(0,0,96),u.Rotator(),False)
report['height_to_saddle']=str(cdo.get_editor_property('HeightToSaddle'))
report['components']=[{'name':c.get_name(),'parent':str(c.get_attach_parent()),'socket':str(c.get_attach_socket_name()),'relative':str(c.get_relative_transform())} for c in bike.get_components_by_class(u.SceneComponent)]
report['sockets']={str(n):str(bike.mesh.get_socket_transform(n,u.RelativeTransformSpace.RTS_ACTOR)) for n in bike.mesh.get_all_socket_names() if any(s in str(n).lower() for s in ['mount','rider','saddle','pelvis','root'])}
for clsname in ['ProceduralMeshLibrary','GeometryScript_AssetUtils','GeometryScript_MeshQueries','StaticMeshEditorSubsystem','SkeletalMesh','SkeletalMeshSocket','Skeleton','AnimBlueprintFactory','AnimGraphNode_ModifyBone','AnimGraphNode_LinkedInputPose','AnimNode_ModifyBone','AnimBlueprintLibrary','SkeletalMeshEditorSubsystem']:
    cls=getattr(u,clsname,None)
    if cls:
        report[clsname]={n:str(getattr(cls,n).__doc__) for n in dir(cls) if any(k in n.lower() for k in ['section_from','vertex','socket','copy_mesh','lod_data','bounds','ref_pose','target_skeleton','bone','post_process','create_skeletal','translation','skeleton'])}
if hasattr(u,'ProceduralMeshLibrary'):
    for i,slot in enumerate(mesh.get_editor_property('static_materials')):
        try:
            verts,tris,normals,uvs,tangents=u.ProceduralMeshLibrary.get_section_from_static_mesh(mesh,0,i)
            vs=[[v.x,v.y,v.z] for v in verts]
            report['parts'].append({'section':i,'slot':str(slot.material_slot_name),'vertices':vs})
        except Exception as ex:report['parts'].append({'section':i,'error':str(ex)})
(ROOT/'evidence/visual_fit_probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] VISUAL FIT PROBE COMPLETE')
