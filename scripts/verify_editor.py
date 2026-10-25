"""Meaningful editor checks: table merges, actual Blueprint execution, and visual components."""
import csv, io, json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
LOCAL='/Game/Mods/SuzumuMotorcycle'
BP=u.BlueprintEditorLibrary
report={'checks':[],'errors':[]}
def check(name,condition,details=None):
    report['checks'].append({'name':name,'passed':bool(condition),'details':details})
    u.log('[SUZUMU] CHECK '+name+' '+('PASS' if condition else 'FAIL'))
def rows(path):
    return list(csv.DictReader(io.StringIO(u.DataTableFunctionLibrary.export_data_table_to_csv_string(u.load_asset(path)))))
def row(path,key): return next(r for r in rows(path) if r['---']==key)
bp=u.load_asset(LOCAL+'/BP_SuzumuMotorcycle')
controller=u.load_asset(LOCAL+'/BP_SuzumuModController')
for obj in [bp,controller]:
    BP.compile_blueprint(obj)
    check(obj.get_name()+' compiles',obj.get_editor_property('status')==u.BlueprintStatus.BS_UP_TO_DATE,str(obj.get_editor_property('status')))
try:
    u.get_default_object(controller.generated_class()).call_method('ModDataTableOperations')
    check('Controller executes table merges',True)
except Exception as ex:
    check('Controller executes table merges',False,str(ex))
manifest=json.loads((ROOT/'evidence/table_manifest.json').read_text(encoding='utf-8'))
for entry in manifest:
    present={r['---'] for r in rows(entry['base'])}
    check('Merged '+entry['base'].rsplit('/',1)[-1],all(k in present for k in entry['rows']))

seat=row('/Game/Items/SaddleTable','19871002')
check('Normal speed 60 km/h',abs(float(seat['RunSpeed'])*.036-60)<.001)
check('Sprint speed 120 km/h',abs(float(seat['SprintSpeed'])*.036-120)<.001)
check('Sprint cost 1/s',float(seat['SprintEnduranceDrain'])==1)
recipe=row('/Game/Items/Recipes/RecipesTable','19871001')
check('Recipe ingredients and station',all(recipe[k]==v for k,v in {'CraftingStations':'18512','Ingredient1ID':'18062','Ingredient1Quantity':'200','Ingredient2ID':'12516','Ingredient2Quantity':'50','Ingredient3ID':'16003','Ingredient3Quantity':'100'}.items()))
feat=row('/Game/Items/Feats/FeatTable','19871001')
check('Feat level, cost, category and parent',feat['LevelRequirement']=='40' and feat['FeatCost']=='25' and feat['Categories']=='(Survival)' and feat['PrerequisiteFeat']=='(41020)')
growth=row('/Game/Systems/Thrall/NPCStatsAndGrowthsDataTable','SuzumuMotorcycle')
check('All starting attributes 15',all(growth[k]=='15' for k in ['BaseStrength','BaseAgility','BaseVitality','BaseAccuracy','BaseEncumbrance','BaseSurvival','BaseGrit']))
stats=[r for r in rows('/Game/Systems/SpawnTable/StatTemplateDataTable') if r['TemplateID']=='SuzumuMotorcycle']
values={(r['Type'],r['StatID']):float(r['Value']) for r in stats}
check('Endurance max 1600 and 10 inventory slots',values.get(('Int','25'))==1600 and values.get(('Int','22'))==10)
spawn=row('/Game/Systems/SpawnTable/SpawnDataTable','SuzumuMotorcycle')
check('Horse growth and built-in seat',spawn['EmbeddedSaddleID']=='19871002' and spawn['MountTypeID']=='Horse' and spawn['LevelCurveID']=='Normal' and spawn['PerkType']=='Hooved')

# Create an unsaved editor world; no existing game map/save is touched.
world=u.EditorLoadingAndSavingUtils.new_blank_map(False)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
bike=actors.spawn_actor_from_class(bp.generated_class(),u.Vector(0,0,100),u.Rotator(),False)
horse_cls=u.EditorAssetLibrary.load_blueprint_class('/Game/Characters/NPCs/Hooved_Wild/Blueprints/BP_NPC_Mounts_Horse_Knight')
horse=actors.spawn_actor_from_class(horse_cls,u.Vector(300,0,100),u.Rotator(),False)
check('Motorcycle instance spawns',bike is not None)
if bike:
    bodies=[c for c in bike.get_components_by_class(u.StaticMeshComponent) if c.get_name().startswith('SuzumuBody')]
    check('Imported motorcycle body present',len(bodies)==1 and bodies[0].get_editor_property('static_mesh') is not None)
    rigs=bike.get_components_by_class(u.SkeletalMeshComponent)
    check('Horse render meshes hidden',all(not c.get_editor_property('render_in_main_pass') for c in rigs if any(k in c.get_name() for k in ['CharacterMesh','Mane','Tail','Penis','Testicles'])))
    fall=u.load_class(None,'/Game/Systems/Progression/DmgTypeHealth_IgnoreArmor_BP_Fall.DmgTypeHealth_IgnoreArmor_BP_Fall_C')
    for label,damage_type in [('fall',fall),('ordinary',u.DamageType)]:
        try:
            base=horse.call_method('ModifyIncomingHealthDamage',(200,damage_type,None,None))
            actual=bike.call_method('ModifyIncomingHealthDamage',(200,damage_type,None,None))
            check(label+' damage execution',actual==(base//2 if label=='fall' else base),{'horse':str(base),'bike':str(actual)})
        except Exception as ex:
            check(label+' damage execution',False,str(ex))
    report['bike_components']=[{'name':c.get_name(),'class':c.get_class().get_path_name()} for c in bike.get_components_by_class(u.ActorComponent)]
report['spawn_api']={name:[m for m in dir(getattr(u,name)) if 'spawn' in m.lower() or 'template' in m.lower()] for name in dir(u) if name in ['ConanGameState','GameSpawnTable','SpawnTable','SpawnTableFunctionLibrary','DreamworldBlueprints','NPCSpawnTable','ConanCharacter']}
report['all_passed']=all(c['passed'] for c in report['checks'])
(ROOT/'evidence/editor_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] VERIFICATION '+str(report['all_passed']))
