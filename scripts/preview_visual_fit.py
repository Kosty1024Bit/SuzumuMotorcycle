"""Render an unsaved fitting scene. No game input, gameplay test, or save changes."""
import builtins
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
bike=builtins._suzumu_visual_bike
floor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,-1),u.Rotator(),False)
floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Plane'))
floor.set_actor_scale3d(u.Vector(20,20,20))
light=actors.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,500),u.Rotator(pitch=-45,yaw=-30,roll=0),False)
light.light_component.set_editor_property('intensity',5.0)
sky=actors.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,500),u.Rotator(),False)
sky.light_component.set_editor_property('intensity',1.0)
# Pose the standard rider for visual fitting, independently from gameplay input.
bike.mesh.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE)
bike.mesh.set_override_post_process_anim_bp(u.load_asset('/Game/Mods/SuzumuMotorcycle/ABP_SuzumuSeatOffset').generated_class(),True)
bike.mesh.set_update_animation_in_editor(True)
rider=actors.spawn_actor_from_class(u.SkeletalMeshActor,u.Vector(),u.Rotator(),False)
comp=rider.skeletal_mesh_component
comp.set_skeletal_mesh_asset(u.load_asset('/Game/Characters/humans/meshes/SK_human_male'))
comp.set_animation_mode(u.AnimationMode.ANIMATION_SINGLE_NODE)
comp.set_animation(u.load_asset('/Game/Characters/humans/animations/mounted/Horse/A_human_mounted_idle_HORSE'))
comp.set_position(0,False)
comp.set_update_animation_in_editor(True)
comp.attach_to_component(bike.mesh,'attachrider',u.AttachmentRule.SNAP_TO_TARGET,u.AttachmentRule.SNAP_TO_TARGET,u.AttachmentRule.KEEP_WORLD,False)
gray=u.load_asset('/Engine/BasicShapes/BasicShapeMaterial')
for i in range(comp.get_num_materials()):comp.set_material(i,gray)
target=u.Vector(0,0,100); camera_pos=u.Vector(290,-420,170)
camera=actors.spawn_actor_from_class(u.CameraActor,camera_pos,u.MathLibrary.find_look_at_rotation(camera_pos,target),False)
camera.camera_component.set_editor_property('field_of_view',45)
u.EditorLevelLibrary.set_level_viewport_camera_info(camera_pos,u.MathLibrary.find_look_at_rotation(camera_pos,target))
# Avoid AutomationLibrary's frame-wait from inside a Slate callback.
capture=actors.spawn_actor_from_class(u.SceneCapture2D,camera_pos,u.MathLibrary.find_look_at_rotation(camera_pos,target),False)
cc=capture.capture_component2d
cc.set_editor_property('fov_angle',45)
rt=u.RenderingLibrary.create_render_target2d(bike,1280,900,u.TextureRenderTargetFormat.RTF_RGBA8)
cc.set_editor_property('texture_target',rt)
cc.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
cc.capture_scene()
u.RenderingLibrary.export_render_target(bike,rt,str(ROOT/'evidence'),'visual_fix_preview.png')
builtins._suzumu_visual_rider=rider
u.log('[SUZUMU] VISUAL FIT PREVIEW REQUESTED')
