import json, re, subprocess, time, urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load current stops
with open('stops.json', encoding='utf-8') as f:
    stops_list = json.load(f)
stops_by_id = {s['id']: s for s in stops_list}

# Load current shapes
with open('shapes.json', encoding='utf-8') as f:
    shapes = json.load(f)

# Fetch LC07A stop sequence from Moovit
def fetch_line(name, lid):
    url = f'https://moovitapp.com/index/en/public_transit-line-{name}-Antalya-3462-3757093-{lid}-0'
    r = subprocess.run(
        ['curl', '-s', '--max-time', '15', '-H', 'User-Agent: Googlebot/2.1', url],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    raw = re.findall(r'(\d{4,6})\s*-\s*([A-Za-zÇçĞğİıÖöŞşÜü][^<\n"]{2,50}?)(?=[<\n"])', r.stdout)
    seen = {}
    for sid, sname in raw:
        if sid not in seen and not sid.startswith('346') and 5000 < int(sid) < 60000:
            seen[sid] = sname.strip()
    return list(seen.items())

print('Fetching LC07A from Moovit...')
stop_pairs = fetch_line('LC07A', '170049960')
print(f'  Got {len(stop_pairs)} stops from Moovit')

# Build ordered shape points
shape_pts = []
matched = 0
for sid, sname in stop_pairs[:90]:
    stop_id = f'ABUS-{sid}'
    if stop_id in stops_by_id:
        s = stops_by_id[stop_id]
        shape_pts.append([s['lat'], s['lng']])
        matched += 1

print(f'  {matched} stops matched to coordinates')

# OSRM routing
def osrm_route_chunk(pts):
    coords = ';'.join(f'{p[1]},{p[0]}' for p in pts)
    url = f'https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read())
    if d.get('code') == 'Ok':
        return [[c[1], c[0]] for c in d['routes'][0]['geometry']['coordinates']]
    return None

print('Routing via OSRM...')
routed = []
i = 0
while i < len(shape_pts) - 1:
    chunk = shape_pts[i:i+10]
    if len(chunk) < 2:
        break
    try:
        r = osrm_route_chunk(chunk)
        if r:
            if routed:
                routed.extend(r[1:])
            else:
                routed.extend(r)
        else:
            routed.extend(chunk)
    except Exception as e:
        print(f'  OSRM error at {i}: {e}')
        routed.extend(chunk)
    i += 9
    time.sleep(0.15)

print(f'  {len(shape_pts)} -> {len(routed)} pts')

# Update shapes.json
shapes['BUS-LC07A'] = routed
with open('shapes.json', 'w', encoding='utf-8') as f:
    json.dump(shapes, f, ensure_ascii=False, separators=(',', ':'))

print(f'shapes.json updated. BUS-LC07A: {len(routed)} pts')
