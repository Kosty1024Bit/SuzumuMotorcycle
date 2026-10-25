"""Create only the mod's new rows, using the installed game's schemas and horse defaults."""
import csv, io, json, sys
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
LOCAL='/Game/Mods/SuzumuMotorcycle'
ID='19871001'
SADDLE='19871002'
MOUNT='SuzumuMotorcycle'
CLASS=LOCAL+'/BP_SuzumuMotorcycle.BP_SuzumuMotorcycle_C'
PATHS={
 'ItemTable':'/Game/Items/ItemTable',
 'RecipesTable':'/Game/Items/Recipes/RecipesTable',
 'FeatTable':'/Game/Items/Feats/FeatTable',
 'FeatTreeTable':'/Game/Systems/Progression/FeatTreeTable',
 'SaddleTable':'/Game/Items/SaddleTable',
 'SpawnDataTable':'/Game/Systems/SpawnTable/SpawnDataTable',
 'ProfessionTemplateDataTable':'/Game/Systems/SpawnTable/ProfessionTemplateDataTable',
 'StatTemplateDataTable':'/Game/Systems/SpawnTable/StatTemplateDataTable',
 'ThrallDataTable':'/Game/Systems/Thrall/ThrallDataTable',
 'NPCStatsAndGrowthsDataTable':'/Game/Systems/Thrall/NPCStatsAndGrowthsDataTable',
 'ItemNameToTemplateID':'/Game/Systems/Survival/Gathering/Gathering_v2/ItemNameToTemplateID',
}
def source(name):
    dt=u.load_asset(PATHS[name]); assert dt, name
    rows=list(csv.DictReader(io.StringIO(u.DataTableFunctionLibrary.export_data_table_to_csv_string(dt))))
    return dt, rows
def clone(name,key):
    _,rs=source(name)
    return dict(next(r for r in rs if r['---']==str(key)))
def text(key,value):
    return 'NSLOCTEXT("SuzumuMotorcycle", "'+key+'", "'+value+'")'
pending={}
item=clone('ItemTable','92229')
item.update({'---':ID,'Name':text('Name','Мотоцикл Suzumu'),'ShortDesc':text('ShortDesc','Одноместный мотоцикл'),'LongDesc':text('LongDesc','Транспорт на основе механики лошади. 10 ячеек, скорость 60 км/ч, спринт 120 км/ч.'),'Icon':LOCAL+'/Art/T_SuzumuIcon.T_SuzumuIcon','SpawnTemplateID':MOUNT,'PerishRate':'0','PerishTo':'0','DLCPackage':'None','MaxStackSize':'1','FirstModifier':text('Mount','Транспорт')})
saddle=clone('ItemTable','2706')
saddle.update({'---':SADDLE,'Name':text('Seat','Встроенное сиденье Suzumu'),'ShortDesc':text('SeatDesc','Встроенное сиденье мотоцикла'),'LongDesc':'','Icon':item['Icon'],'VisualSkeletalMesh':'None','VisualStaticMesh':'None','DLCPackage':'None','ArmourValue':'0','MaxDurability':'0','RepairItem1':'0','RepairItem2':'0','RepairItem3':'0','PerishRate':'0','PerishTo':'0'})
pending['ItemTable']=[item,saddle]
recipe=clone('RecipesTable','1590')
recipe.update({'---':ID,'RecipeName':item['Name'],'ShortDesc':item['ShortDesc'],'RecipeType':'Utility','ConstructionSubClass':'None','CraftingStations':'18512','TimeToCraft':'60','CraftXP':'1000','Icon':item['Icon'],'Ingredient1ID':'18062','Ingredient1Quantity':'200','Ingredient2ID':'12516','Ingredient2Quantity':'50','Ingredient3ID':'16003','Ingredient3Quantity':'100','Ingredient4ID':'0','Ingredient4Quantity':'0','Result1ID':ID,'Result1Quantity':'1','IsRecipeEnabled':'True','DLCPackage':'None'})
pending['RecipesTable']=[recipe]
feat=clone('FeatTable','41020')
feat.update({'---':ID,'FeatName':text('Feat','Механик Suzumu'),'Description':text('FeatDesc','Позволяет создать мотоцикл на верстаке умельца.'),'LevelRequirement':'40','FeatCost':'25','Categories':'(Survival)','PrerequisiteFeat':'(41020)','RewardRecipe':'('+ID+')','Icon':item['Icon'],'GiveOnSpawn':'False','AutoLearnDlcFeat':'False','CornerStoneLevel':'0','DLCPackage':'None'})
pending['FeatTable']=[feat]
tree=clone('FeatTreeTable','41020')
tree.update({'---':ID,'GiveOnSpawn':'False','LevelRequirement':'40','FeatCost':'25','PrerequisiteFeat':'("41020")','RewardRecipe':'("'+ID+'")'})
pending['FeatTreeTable']=[tree]
seat=clone('SaddleTable','2706')
seat.update({'---':SADDLE,'TargetCharacter':CLASS,'WalkSpeed':'1666.666667','RunSpeed':'1666.666667','SprintSpeed':'3333.333333','SprintEnduranceDrain':'1','HideMane':'True','HideTail':'True'})
pending['SaddleTable']=[seat]
spawn=clone('SpawnDataTable','Horse_Knight')
spawn.update({'---':MOUNT,'Name':item['Name'],'NPCClass':CLASS,'ProfessionTemplate':MOUNT,'StatTemplate':MOUNT,'GrowthID':MOUNT,'EmbeddedSaddleID':SADDLE,'MountTypeID':'Horse'})
pending['SpawnDataTable']=[spawn]
profession=clone('ProfessionTemplateDataTable','Horse_Knight')
profession.update({'---':MOUNT,'ThrallType':ID,'Icon':item['Icon']})
pending['ProfessionTemplateDataTable']=[profession]
thrall=clone('ThrallDataTable','110')
thrall.update({'---':ID,'ThrallActor':CLASS})
pending['ThrallDataTable']=[thrall]
growth=clone('NPCStatsAndGrowthsDataTable','Horse_Knight')
growth.update({'---':MOUNT,'RowType':MOUNT})
for k in ['BaseStrength','BaseAgility','BaseVitality','BaseAccuracy','BaseEncumbrance','BaseSurvival','BaseGrit']: growth[k]='15'
pending['NPCStatsAndGrowthsDataTable']=[growth]
_,base_stats=source('StatTemplateDataTable')
stats=[]
for idx,r in enumerate(r for r in base_stats if r['TemplateID']=='Animal Base'):
    r=dict(r); r.update({'---':str(int(ID)+100+idx),'TemplateID':MOUNT}); stats.append(r)
for idx,(stat,value) in enumerate([(24,1600),(25,1600),(22,10),(5,1600),(6,1600)]):
    stats.append({'---':str(int(ID)+200+idx),'TemplateID':MOUNT,'Type':'Int','StatID':str(stat),'Value':str(value)})
pending['StatTemplateDataTable']=stats
pending['ItemNameToTemplateID']=[{'---':MOUNT,'ID_XX':ID},{'---':'SuzumuMotorcycleSeat','ID_XX':SADDLE}]
manifest=[]
for name,rows in pending.items():
    base,existing=source(name)
    occupied={r['---'] for r in existing}
    # The verification controller may already have merged our rows in this editor session.
    old_manifest=ROOT/'evidence/table_manifest.json'
    if old_manifest.exists():
        for entry in json.loads(old_manifest.read_text(encoding='utf-8')):
            if entry['base']==PATHS[name]: occupied.difference_update(entry['rows'])
    assert not any(r['---'] in occupied for r in rows), 'ID collision in '+name
    path=LOCAL+'/Data/DT_Suzumu_'+name
    if u.EditorAssetLibrary.does_asset_exist(path):
        dt=u.load_asset(path)
    else:
        factory=u.DataTableFactory()
        factory.set_editor_property('struct',u.DataTableFunctionLibrary.get_data_table_row_struct(base))
        dt=u.AssetToolsHelpers.get_asset_tools().create_asset(path.rsplit('/',1)[-1],path.rsplit('/',1)[0],u.DataTable,factory)
    assert dt, 'Create failed: '+path
    stream=io.StringIO(); writer=csv.DictWriter(stream,fieldnames=list(existing[0])); writer.writeheader(); writer.writerows(rows)
    assert u.DataTableFunctionLibrary.fill_data_table_from_csv_string(dt,stream.getvalue()), 'Import failed: '+name
    assert len(u.DataTableFunctionLibrary.get_data_table_row_names(dt))==len(rows)
    assert u.EditorAssetLibrary.save_loaded_asset(dt), 'Save failed: '+path
    manifest.append({'base':PATHS[name],'mod':path,'rows':[r['---'] for r in rows]})
    u.log('[SUZUMU] TABLE CREATED '+name+' rows='+str(len(rows)))
(ROOT/'evidence/table_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
