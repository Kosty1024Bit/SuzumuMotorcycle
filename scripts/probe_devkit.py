import json
from pathlib import Path
import unreal as u
import runpy

JOB = Path(__file__).resolve().parents[1] / 'job.json'
if JOB.exists():
    job = json.loads(JOB.read_text(encoding='utf-8'))
    runpy.run_path(str(Path(__file__).parent / job['script']), run_name='__main__')
    raise SystemExit(0)

OUT = Path(r'C:/Users/konst/Documents/ChatGPT/universal-modder/SuzumuMotorcycle/evidence')
OUT.mkdir(parents=True, exist_ok=True)
def log(s):
    u.log('[SUZUMU] ' + str(s))

reg = u.AssetRegistryHelpers.get_asset_registry()
reg.search_all_assets(True)
assets = reg.get_assets_by_path('/Game', recursive=True)
found = []
for a in assets:
    p = str(a.package_name)
    name = str(a.asset_name)
    if (('horse' in p.lower() and ('blueprint' in p.lower() or name.startswith('BP_')))
        or name in ['MountTable', 'MountMovementRatesTable', 'ItemTable', 'RecipesTable', 'FeatTable', 'FeatTreeTable',
                    'ThrallDataTable', 'NPCStatsAndGrowthsDataTable', 'NPCLevelCurveDataTable', 'SpawnDataTable',
                    'StatTemplateDataTable', 'StatModifierTemplateDataTable', 'SaddleTable']):
        found.append({'path':p,'class':str(a.asset_class_path)})
(OUT/'assets.json').write_text(json.dumps(found,indent=2),encoding='utf-8')
for a in found:
    p = a['path']
    obj = u.load_asset(p)
    if isinstance(obj, u.DataTable):
        csv = u.DataTableFunctionLibrary.export_data_table_to_csv_string(obj)
        (OUT/(p.rsplit('/',1)[-1]+'.csv')).write_text(csv,encoding='utf-8')
        log('TABLE '+p+' rows='+str(len(u.DataTableFunctionLibrary.get_data_table_row_names(obj))))
    elif isinstance(obj, u.Blueprint):
        cls = u.EditorAssetLibrary.load_blueprint_class(p)
        cdo = u.get_default_object(cls)
        (OUT/(p.rsplit('/',1)[-1]+'.txt')).write_text('\n'.join(dir(cdo)),encoding='utf-8')
        if hasattr(u, 'ToolsetLibrary'):
            props = u.ToolsetLibrary.list_struct_properties(cls)
            (OUT/(p.rsplit('/',1)[-1]+'.properties.json')).write_text(props,encoding='utf-8')
        log('BLUEPRINT '+p+' '+str(cls))
(OUT/'api.json').write_text(json.dumps({n:[x for x in dir(getattr(u,n,None)) if not x.startswith('_')] for n in ['BlueprintGraphEditor','BlueprintEditorLibrary','SubobjectDataSubsystem','SubobjectDataBlueprintFunctionLibrary','EditorAssetLibrary','DataTableFunctionLibrary','Object','Exporter','BlueprintFactory','PythonScriptLibrary']},indent=2),encoding='utf-8')
log('PROBE COMPLETE')
