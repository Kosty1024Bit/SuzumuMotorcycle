import json
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parents[1]
docs={}
for name in ['EditorLevelLibrary','LevelEditorSubsystem','LevelEditorPlaySettings','AutomationLibrary','GamePlaySettings','EditorUtilitySubsystem','ConanGameMode','GameplayStatics']:
    cls=getattr(u,name,None)
    if cls:
        docs[name]={n:str(getattr(cls,n).__doc__) for n in dir(cls) if any(t in n.lower() for t in ['play','world','screenshot','spawn','template'])}
(ROOT/'evidence/gui_api.json').write_text(json.dumps(docs,indent=2),encoding='utf-8')
u.log('[SUZUMU] GUI API READY')
