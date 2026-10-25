import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def rows(n):
    return list(csv.DictReader((ROOT/'evidence'/f'{n}.csv').open(encoding='utf-8-sig')))
def show(n, selected, keys=None):
    print('\n'+n)
    print(json.dumps([{k:r[k] for k in (keys or r.keys())} for r in selected],ensure_ascii=False,indent=2))
data=rows('ItemTable')
show('ItemTable',[r for r in data if r['---']=='92229' or any(x in r['Name'] for x in ['Hardened Steel Bar','Steel Reinforcement','Leather','Artisan'])],['---','Name','ItemClass','VisualObject','SpawnTemplateID','ItemContainerSize'])
for n,key in [('ThrallDataTable','Horse_Knight'),('NPCStatsAndGrowthsDataTable','Horse_Knight'),('FeatTable','41020'),('RecipesTable','41020')]:
    show(n,[r for r in rows(n) if r['---']==key])
show('StatTemplateDataTable',[r for r in rows('StatTemplateDataTable') if r['TemplateID']=='Animal Base'])
show('MountTable',[{k:v for k,v in rows('MountTable')[0].items() if 'Anim' not in k}])
show('FeatTreeTable',rows('FeatTreeTable')[:2])
print('\nRecipesTable fields:',list(rows('RecipesTable')[0]))
