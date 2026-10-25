"""Read the supplied binary FBX without executing third-party model tools."""
import array
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'Suzumu Bike 3D Model/CQ77Z1SHGEKYVB0JPDH2Y9QG1_FBX/CQ77Z1SHGEKYVB0JPDH2Y9QG1.fbx'
DATA = SOURCE.read_bytes()
assert DATA[:23] == b'Kaydara FBX Binary  \x00\x1a\x00'
VERSION = struct.unpack_from('<I', DATA, 23)[0]
FMT = '<QQQB' if VERSION >= 7500 else '<IIIB'
HEADER = struct.calcsize(FMT)
TYPES = {'Y': 'h', 'C': '?', 'I': 'i', 'F': 'f', 'D': 'd', 'L': 'q'}

def prop(pos):
    typ = chr(DATA[pos]); pos += 1
    if typ in TYPES:
        fmt = '<' + TYPES[typ]
        return struct.unpack_from(fmt, DATA, pos)[0], pos + struct.calcsize(fmt)
    if typ in 'SR':
        size = struct.unpack_from('<I', DATA, pos)[0]; pos += 4
        raw = DATA[pos:pos+size]
        return (raw.decode('utf-8', errors='replace') if typ == 'S' else raw.hex()), pos+size
    if typ in 'fdlibc':
        size, encoding, packed = struct.unpack_from('<III', DATA, pos); pos += 12
        raw = DATA[pos:pos+packed]
        if encoding: raw = zlib.decompress(raw)
        values = array.array({'f':'f','d':'d','l':'q','i':'i','b':'b','c':'b'}[typ])
        values.frombytes(raw)
        assert len(values) == size
        return list(values), pos+packed
    raise ValueError(typ)

def node(pos):
    end, count, _, name_len = struct.unpack_from(FMT, DATA, pos)
    if end == 0: return None, pos + HEADER
    pos += HEADER
    name = DATA[pos:pos+name_len].decode(); pos += name_len
    props = []
    for _ in range(count):
        value, pos = prop(pos); props.append(value)
    children = []
    while pos + HEADER <= end:
        child, pos = node(pos)
        if child is None: break
        children.append(child)
    return {'name': name, 'properties': props, 'children': children}, end

def descendants(nodes):
    for n in nodes:
        yield n
        yield from descendants(n['children'])

nodes=[]; pos=27
while pos+HEADER < len(DATA):
    n,pos=node(pos)
    if n is None: break
    nodes.append(n)
report={'source': str(SOURCE), 'version': VERSION, 'objects': [], 'global_settings': [], 'connections': []}
for n in descendants(nodes):
    if n['name'] in ('Geometry','Model','Material','Texture','Video'):
        entry={'type':n['name'],'properties':n['properties'],'settings':[]}
        for c in descendants(n['children']):
            if c['name']=='Vertices':
                verts=c['properties'][0]
                entry['vertices']=len(verts)//3
                entry['min']=[min(verts[a::3]) for a in range(3)]
                entry['max']=[max(verts[a::3]) for a in range(3)]
            elif c['name'] in ('P','FileName','RelativeFilename'):
                entry['settings'].append(c['properties'])
        report['objects'].append(entry)
    elif n['name']=='GlobalSettings':
        report['global_settings']=[c['properties'] for c in descendants(n['children']) if c['name']=='P']
    elif n['name']=='Connections':
        report['connections']=[c['properties'] for c in n['children'] if c['name']=='C']
dest=ROOT/'evidence/model_inspection.json'; dest.parent.mkdir(exist_ok=True)
dest.write_text(json.dumps(report,indent=2),encoding='utf-8')
geometries=[o for o in report['objects'] if o['type']=='Geometry']
print(json.dumps({'fbx_version':VERSION,'geometries':len(geometries),'vertices':sum(o['vertices'] for o in geometries),'report':str(dest)},indent=2))
