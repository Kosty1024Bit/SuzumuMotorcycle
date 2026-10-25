import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
report={}
for name in dir(u):
    if not any(t in name for t in ['Spawn','Thrall','NPC','Npc']): continue
    obj=getattr(u,name)
    if not isinstance(obj,type): continue
    methods={n:str(getattr(obj,n).__doc__) for n in dir(obj) if any(t in n.lower() for t in ['spawn_npc','spawn_thrall','spawn_from','spawn_character','create_thrall','create_npc','place_thrall','initialize_from','spawn_actor','spawn_pet'])}
    if methods: report[name]=methods
for name in ['ConanGameState','ThrallItem','ConanCharacter','StatHolder']:
    obj=getattr(u,name,None)
    if obj:
        report[name]={n:str(getattr(obj,n).__doc__) for n in dir(obj) if any(t in n.lower() for t in ['spawn','thrall','template','item_id']) and not n.startswith('_')}
(ROOT/'evidence/spawn_api.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] SPAWN API READY')
