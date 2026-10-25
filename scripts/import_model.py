"""Import the supplied FBX and local textures; create materials without web texture fetches."""
import json, re
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'Suzumu Bike 3D Model/CQ77Z1SHGEKYVB0JPDH2Y9QG1_FBX'
ART='/Game/Mods/SuzumuMotorcycle/Art'
AT=u.AssetToolsHelpers.get_asset_tools()
def log(s): u.log('[SUZUMU] '+str(s))
def import_file(src,name,options=None,factory=None):
    task=u.AssetImportTask()
    task.filename=str(src); task.destination_path=ART; task.destination_name=name
    task.automated=True; task.replace_existing=True; task.save=True
    if options: task.options=options
    if factory: task.factory=factory
    AT.import_asset_tasks([task])
    imported=list(task.imported_object_paths)
    assert imported, 'Import failed '+str(src)
    return [u.load_asset(p) for p in imported]
textures={}
for file in SOURCE.glob('*.png'):
    name='T_Suzumu_'+re.sub(r'[^a-zA-Z0-9_]','_',file.stem)
    path=ART+'/'+name
    tex=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else import_file(file,name)[0]
    assert isinstance(tex,u.Texture2D)
    if file.stem.endswith('_n'):
        tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb',False)
    u.EditorAssetLibrary.save_loaded_asset(tex)
    textures[file.name]=tex
icon_path=ART+'/T_SuzumuIcon'
icon=u.load_asset(icon_path) if u.EditorAssetLibrary.does_asset_exist(icon_path) else import_file(SOURCE/'CQ77Z1SHGEKYVB0JPDH2Y9QG1.jpg','T_SuzumuIcon')[0]
icon.set_editor_property('lod_group',u.TextureGroup.TEXTUREGROUP_UI)
icon.set_editor_property('mip_gen_settings',u.TextureMipGenSettings.TMGS_NO_MIPMAPS)
u.EditorAssetLibrary.save_loaded_asset(icon)
mesh_path=ART+'/SM_SuzumuMotorcycle'
if u.EditorAssetLibrary.does_asset_exist(mesh_path) and not (ROOT/'evidence/force_reimport').exists():
    mesh=u.load_asset(mesh_path)
else:
    opts=u.FbxImportUI()
    opts.set_editor_property('automated_import_should_detect_type',False)
    opts.set_editor_property('mesh_type_to_import',u.FBXImportType.FBXIT_STATIC_MESH)
    opts.set_editor_property('import_as_skeletal',False)
    opts.set_editor_property('import_mesh',True)
    opts.set_editor_property('import_materials',False)
    opts.set_editor_property('import_textures',False)
    data=opts.static_mesh_import_data
    data.set_editor_property('combine_meshes',True)
    data.set_editor_property('import_uniform_scale',88.0)
    data.set_editor_property('convert_scene',True)
    data.set_editor_property('import_rotation',u.Rotator(pitch=0,yaw=180,roll=0))
    # FBX is centered about its axle plane; put the bottom of the tyres on local Z=0.
    data.set_editor_property('import_translation',u.Vector(0,0,61.69917536))
    meshes=import_file(SOURCE/'CQ77Z1SHGEKYVB0JPDH2Y9QG1.fbx','SM_SuzumuMotorcycle',opts,u.FbxFactory())
    mesh=next(x for x in meshes if isinstance(x,u.StaticMesh))
assert isinstance(mesh,u.StaticMesh)
report=json.loads((ROOT/'evidence/model_inspection.json').read_text(encoding='utf-8'))
objects={o['properties'][0]:o for o in report['objects']}
materials={}
for mid,m in objects.items():
    if m['type']!='Material': continue
    original=m['properties'][1].split('\x00')[0]
    material_name='M_Suzumu_'+re.sub(r'[^a-zA-Z0-9_]','_',original)
    path=ART+'/'+material_name
    mat=u.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else AT.create_asset(material_name,ART,u.Material,u.MaterialFactoryNew())
    u.MaterialEditingLibrary.delete_all_material_expressions(mat)
    diffuse=None; normal=None
    for c in report['connections']:
        if len(c)<4 or c[2]!=mid or c[1] not in objects: continue
        tex_obj=objects[c[1]]
        if tex_obj['type']!='Texture': continue
        refs=[x[0].replace('\\','/').rsplit('/',1)[-1] for x in tex_obj['settings'] if len(x)==1 and isinstance(x[0],str)]
        texture=next((textures[r] for r in refs if r in textures),None)
        if texture:
            if c[3] in ['NormalMap','Bump']: normal=texture
            elif c[3]=='DiffuseColor': diffuse=texture
    if diffuse:
        sample=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionTextureSample,-350,0)
        sample.texture=diffuse
        u.MaterialEditingLibrary.connect_material_property(sample,'RGB',u.MaterialProperty.MP_BASE_COLOR)
    else:
        color=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant3Vector,-350,0)
        color.set_editor_property('constant',u.LinearColor(.35,.35,.35,1))
        u.MaterialEditingLibrary.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
    if normal:
        sample=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionTextureSample,-350,220)
        sample.texture=normal; sample.sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL
        u.MaterialEditingLibrary.connect_material_property(sample,'RGB',u.MaterialProperty.MP_NORMAL)
    rough=u.MaterialEditingLibrary.create_material_expression(mat,u.MaterialExpressionConstant,-350,440)
    rough.r=.8 if diffuse and 'tyre' in diffuse.get_name() else .5
    u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
    u.MaterialEditingLibrary.recompile_material(mat)
    u.EditorAssetLibrary.save_loaded_asset(mat)
    materials[original]=mat
slots=[]
for index,slot in enumerate(mesh.get_editor_property('static_materials')):
    slot_name=str(slot.get_editor_property('material_slot_name'))
    candidates=[mat for name,mat in materials.items() if name.lower()==slot_name.lower()]
    if not candidates:
        normalized=re.sub(r'[^a-z0-9]','',slot_name.lower())
        candidates=[mat for name,mat in materials.items() if re.sub(r'[^a-z0-9]','',name.lower())==normalized]
    assert candidates, 'Unresolved material slot '+slot_name
    mesh.set_material(index,candidates[0]); slots.append({'index':index,'slot':slot_name,'material':candidates[0].get_path_name()})
u.EditorAssetLibrary.save_loaded_asset(mesh)
(ROOT/'evidence/imported_model.json').write_text(json.dumps({'mesh':mesh.get_path_name(),'bounds':str(mesh.get_bounds()),'slots':slots},indent=2),encoding='utf-8')
log('MODEL IMPORTED '+mesh.get_path_name())
