import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
anim=u.load_asset('/Game/Characters/humans/animations/mounted/Horse/A_human_mounted_idle_HORSE')
pose=u.AnimPoseExtensions.get_anim_pose_at_time(anim,0.0,u.AnimPoseEvaluationOptions())
names=[str(n) for n in u.AnimPoseExtensions.get_bone_names(pose)]
data={'human_bones':{n:str(u.AnimPoseExtensions.get_bone_pose(pose,n,u.AnimPoseSpaces.WORLD)) for n in names if any(k in n.lower() for k in ['pelvis','root','spine_01','thigh','foot'])}}
player=u.get_default_object(u.load_asset('/Game/Characters/BasePlayerChar').generated_class())
bike=u.get_default_object(u.load_asset('/Game/Mods/SuzumuMotorcycle/BP_SuzumuMotorcycle').generated_class())
data['player_mesh_relative']=str(player.mesh.get_relative_transform())
rig=bike.mesh.get_editor_property('skeletal_mesh_asset')
data['horse_mesh']=rig.get_path_name()
s=rig.find_socket('attachrider')
data['socket']={n:str(s.get_editor_property(n)) for n in ['socket_name','bone_name','relative_location','relative_rotation']}
data['reference_pose_api']=str(u.AnimPoseExtensions.get_reference_pose.__doc__) if hasattr(u.AnimPoseExtensions,'get_reference_pose') else None
data['screenshot_api']=str(u.AutomationLibrary.take_high_res_screenshot.__doc__)
data['animations']=[str(a.package_name) for a in u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game/Characters/NPCs/Hooved_Wild',True) if 'idle' in str(a.asset_name).lower() and 'horse' in str(a.asset_name).lower()][:30]
(ROOT/'evidence/rider_pose_fit.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
u.log('[SUZUMU] MOUNTED HUMAN POSE SAMPLED')
