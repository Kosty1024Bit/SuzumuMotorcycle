"""Lower only the rider attachment bone. No base mesh or locomotion graph is copied."""
import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
LOCAL='/Game/Mods/SuzumuMotorcycle'
BP=u.BlueprintEditorLibrary
bike=u.get_default_object(u.load_asset(LOCAL+'/BP_SuzumuMotorcycle').generated_class())
rig=bike.mesh.get_editor_property('skeletal_mesh_asset')
factory=u.AnimBlueprintFactory()
factory.set_editor_property('target_skeleton',rig.get_editor_property('skeleton'))
name='ABP_SuzumuSeatOffset'
abp=u.load_asset(LOCAL+'/'+name) if u.EditorAssetLibrary.does_asset_exist(LOCAL+'/'+name) else u.AssetToolsHelpers.get_asset_tools().create_asset(name,LOCAL,u.AnimBlueprint,factory)
assert abp
g=BP.find_graph(abp,'AnimGraph'); assert g
ed=u.BlueprintGraphEditor.get_graph_editor(g)
root=next(n for n in ed.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_Root')
ed.remove_nodes([n for n in ed.list_all_nodes() if n!=root])
created={}
for key,path in [('input','Animation|LinkedAnimGraphs|InputPose'),('to_component','Animation|ConvertSpaces|LocalToComponent'),('offset','Animation|SkeletalControls|Transform(Modify)Bone'),('to_local','Animation|ConvertSpaces|ComponentToLocal')]:
    n=ed.create_node_from_name(path,u.Vector2D(0,0),[]); assert n,path
    created[key]=n
offset=created['offset']
node=offset.get_editor_property('node')
bone=u.BoneReference()
bone.set_editor_property('bone_name','b_attachrider')
node.set_editor_property('bone_to_modify',bone)
# The horse mesh has yaw -90: component Y is actor X. Keep the pose, rotation
# and scale of every other bone unchanged. Seat height is ~93 cm above ground.
node.set_editor_property('translation',u.Vector(0,-10,-110))
node.set_editor_property('translation_mode',u.BoneModificationMode.BMM_ADDITIVE)
node.set_editor_property('translation_space',u.BoneControlSpace.BCS_COMPONENT_SPACE)
offset.set_editor_property('node',node)
assert BP.find_input_pin(offset,'Translation').set_pin_value('0,-10,-110')
def link(a,op,b,ip):
    assert BP.find_output_pin(a,op).try_create_connection(BP.find_input_pin(b,ip)),op+' -> '+ip
link(created['input'],'Pose',created['to_component'],'LocalPose')
link(created['to_component'],'ComponentPose',offset,'ComponentPose')
link(offset,'Pose',created['to_local'],'ComponentPose')
link(created['to_local'],'Pose',root,'Result')
for i,n in enumerate([created['input'],created['to_component'],offset,created['to_local'],root]):
    BP.set_node_pos(n,u.IntPoint(i*280,0))
assert BP.compile_blueprint(abp)
assert abp.get_editor_property('status')==u.BlueprintStatus.BS_UP_TO_DATE,str(abp.get_editor_property('status'))
u.EditorAssetLibrary.save_loaded_asset(abp)
report={'blueprint':abp.get_path_name(),'bone':'b_attachrider','component_offset_cm':[0,-10,-110],'actor_offset_cm':[-10,0,-110],'status':str(abp.get_editor_property('status'))}
(ROOT/'evidence/seat_pose_built.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] SEAT OFFSET COMPILED')
