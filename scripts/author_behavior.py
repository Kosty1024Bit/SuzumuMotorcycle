"""Horse subclass behavior, visual component and additive table controller."""
import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
LOCAL='/Game/Mods/SuzumuMotorcycle'
BP=u.BlueprintEditorLibrary
def log(s): u.log('[SUZUMU] '+str(s))
def inp(node,name):
    p=BP.find_input_pin(node,name); assert p.is_valid(), node.get_name()+' input '+name
    return p
def out(node,name):
    p=BP.find_output_pin(node,name); assert p.is_valid(), node.get_name()+' output '+name
    return p
def link(a,b): assert a.try_create_connection(b), 'Cannot connect '+str(a)+' to '+str(b)
def literal(node,name,value): assert inp(node,name).set_pin_value(str(value)), 'Invalid '+name+'='+str(value)
def call(ed,path):
    n=ed.add_call_function_node(path); assert n, path
    return n
def graph_nodes(bp,name):
    g=BP.find_graph(bp,name); assert g,name
    ed=u.BlueprintGraphEditor.get_graph_editor(g)
    return g,ed,list(ed.list_all_nodes())
def clean_override(bp,name):
    g=BP.add_function_override(bp,name); assert g,name
    ed=u.BlueprintGraphEditor.get_graph_editor(g)
    nodes=list(ed.list_all_nodes())
    keep=[n for n in nodes if n.get_class().get_name() in ['K2Node_FunctionEntry','K2Node_FunctionResult','K2Node_CallParentFunction']]
    ed.remove_nodes([n for n in nodes if n not in keep])
    return g,ed,keep

bp=u.load_asset(LOCAL+'/BP_SuzumuMotorcycle'); assert bp
# Preserve the horse's fall rules; halve only incoming fall health damage after its calculation.
BP.remove_function_graph(bp,'GetFallDamageReduction')
g,ed,nodes=clean_override(bp,'ModifyIncomingHealthDamage')
entry=next(n for n in nodes if n.get_class().get_name()=='K2Node_FunctionEntry')
parent=next(n for n in nodes if n.get_class().get_name()=='K2Node_CallParentFunction')
result=next(n for n in nodes if n.get_class().get_name()=='K2Node_FunctionResult')
isa=call(ed,'/Script/Engine.KismetMathLibrary:ClassIsChildOf')
link(out(entry,'DamageType'),inp(isa,'TestClass'))
literal(isa,'ParentClass','/Game/Systems/Progression/DmgTypeHealth_IgnoreArmor_BP_Fall.DmgTypeHealth_IgnoreArmor_BP_Fall_C')
half=call(ed,'/Script/Engine.KismetMathLibrary:Divide_IntInt')
link(out(parent,'NewDamageValue'),inp(half,'A')); literal(half,'B','2')
select=call(ed,'/Script/Engine.KismetMathLibrary:SelectInt')
link(out(half,'ReturnValue'),inp(select,'A'))
link(out(parent,'NewDamageValue'),inp(select,'B'))
link(out(isa,'ReturnValue'),inp(select,'bPickA'))
inp(result,'NewDamageValue').break_pin_links()
link(out(select,'ReturnValue'),inp(result,'NewDamageValue'))

# New mesh belongs to the child, attached to the character capsule; the horse rig stays for riding.
sds=u.get_engine_subsystem(u.SubobjectDataSubsystem)
S=u.SubobjectDataBlueprintFunctionLibrary
handles=list(sds.k2_gather_subobject_data_for_blueprint(bp))
root=next(h for h in handles if S.is_root_component(S.get_data(h)))
visual=None
for h in handles:
    sd=S.get_data(h)
    if str(S.get_variable_name(sd))=='SuzumuBody': visual=S.get_associated_object(sd)
if visual is None:
    handle,reason=sds.add_new_subobject(u.AddNewSubobjectParams(parent_handle=root,new_class=u.StaticMeshComponent,blueprint_context=bp))
    assert reason.is_empty(),str(reason)
    sds.rename_subobject(handle,u.Text('SuzumuBody'))
    visual=S.get_associated_object(S.get_data(handle))
assert visual
visual.set_editor_property('static_mesh',u.load_asset(LOCAL+'/Art/SM_SuzumuMotorcycle'))
visual.set_editor_property('relative_location',u.Vector(0,0,-96))
visual.set_collision_profile_name('NoCollision')
visual.set_editor_property('mobility',u.ComponentMobility.MOVABLE)

# Construction runs on placed instances and clients. Rendering flags survive horse visibility toggles.
g,ed,nodes=graph_nodes(bp,'UserConstructionScript')
keep=[n for n in nodes if n.get_class().get_name() in ['K2Node_FunctionEntry','K2Node_CallParentFunction']]
ed.remove_nodes([n for n in nodes if n not in keep])
entry=next(n for n in keep if n.get_class().get_name()=='K2Node_FunctionEntry')
parents=[n for n in keep if n.get_class().get_name()=='K2Node_CallParentFunction']
last=out(parents[0],'then') if parents else out(entry,'then')
for member in ['Mesh','Mane','Tail','Penis','Testicles']:
    getter=ed.add_get_member_variable_node(member)
    assert getter,member
    target=out(getter,member)
    for function,pin,value in [('SetRenderInMainPass','bValue','false'),('SetRenderInDepthPass','bValue','false'),('SetCastShadow','NewCastShadow','false')]:
        node=call(ed,'/Script/Engine.PrimitiveComponent:'+function)
        link(target,inp(node,'self')); literal(node,pin,value)
        link(last,inp(node,'execute')); last=out(node,'then')
for member in ['LetfFootAudioComp','RightFootAudioComp','VoiceAudioComp','NPC_Monster_Breath']:
    getter=ed.add_get_member_variable_node(member)
    if not getter: continue
    node=call(ed,'/Script/Engine.AudioComponent:SetVolumeMultiplier')
    link(out(getter,member),inp(node,'self')); literal(node,'NewVolumeMultiplier','0')
    link(last,inp(node,'execute')); last=out(node,'then')

BP.compile_blueprint(bp)
assert bp.get_editor_property('status') in [u.BlueprintStatus.BS_UP_TO_DATE,u.BlueprintStatus.BS_UP_TO_DATE_WITH_WARNINGS],str(bp.get_editor_property('status'))
cdo=u.get_default_object(bp.generated_class())
cdo.set_editor_property('DefaultStamina',1600)
cdo.set_editor_property('HeightToSaddle',120.0)
assert cdo.mesh.get_outer()==cdo
cdo.mesh.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
u.EditorAssetLibrary.save_loaded_asset(bp)
log('MOTORCYCLE BEHAVIOR COMPILED')

controller=u.load_asset(LOCAL+'/BP_SuzumuModController'); assert controller
g,ed,nodes=graph_nodes(controller,'ModDataTableOperations')
entry=next(n for n in nodes if n.get_class().get_name()=='K2Node_FunctionEntry')
ed.remove_nodes([n for n in nodes if n!=entry])
last=out(entry,'then')
manifest=json.loads((ROOT/'evidence/table_manifest.json').read_text(encoding='utf-8'))
for table in manifest:
    node=ed.create_node_from_name('Mods|DataTableModification|MergeDataTables',u.Vector2D(0,0),[])
    assert node
    literal(node,'MergeIntoDataTable',table['base']+'.'+table['base'].rsplit('/',1)[-1])
    literal(node,'ToBeAddedDataTable',table['mod']+'.'+table['mod'].rsplit('/',1)[-1])
    link(last,inp(node,'execute')); last=out(node,'then')
BP.compile_blueprint(controller)
assert controller.get_editor_property('status') in [u.BlueprintStatus.BS_UP_TO_DATE,u.BlueprintStatus.BS_UP_TO_DATE_WITH_WARNINGS],str(controller.get_editor_property('status'))
u.EditorAssetLibrary.save_loaded_asset(controller)
log('MOD CONTROLLER COMPILED; MERGES='+str(len(manifest)))
(ROOT/'evidence/behavior_built.json').write_text(json.dumps({'motorcycle':str(bp.get_editor_property('status')),'controller':str(controller.get_editor_property('status')),'table_merges':len(manifest)},indent=2),encoding='utf-8')
