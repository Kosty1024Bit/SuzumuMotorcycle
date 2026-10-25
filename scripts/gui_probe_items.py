import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
report={}
for name in ['GameItemSpawner','ThrallSystemComponent','ItemInventory','GameItem','ThrallItem','ConanCharacter','ConanPlayerController']:
    cls=getattr(u,name,None)
    if cls:
        report[name]={n:str(getattr(cls,n).__doc__) for n in dir(cls) if any(t in n.lower() for t in ['spawn','create','add_item','mount','saddle','thrall','initialize','setup','possess']) and not n.startswith('_')}
(ROOT/'evidence/item_spawn_api.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] ITEM SPAWN API READY')
