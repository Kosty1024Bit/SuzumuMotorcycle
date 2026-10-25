import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
report={}
for cls in [u.World,u.GameplayStatics,u.GameItemSpawner,u.PlayerController,u.ConanGameState]:
    report[cls.__name__]={n:str(getattr(cls,n).__doc__) for n in dir(cls) if any(t in n.lower() for t in ['spawn','possess','player_controller','spectat']) and not n.startswith('_')}
world=u.EditorLevelLibrary.get_game_world()
pc=u.GameplayStatics.get_player_controller(world,0)
report['controller']=str(pc)
report['controller_pawn']=str(u.GameplayStatics.get_player_pawn(world,0)) if pc else None
report['controller_functions']=[str(x) for x in u.BlueprintEditorLibrary.list_functions(u.load_asset('/Game/Systems/BaseGameMode')) if 'spawn' in str(x).lower() or 'create' in str(x).lower()]
(ROOT/'evidence/world_spawn_api.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('[SUZUMU] WORLD API READY')
