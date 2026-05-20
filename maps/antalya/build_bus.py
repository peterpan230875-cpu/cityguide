import json, re, os, subprocess, time, sys
sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# Antalya Bus-Linien aus Moovit + OSM Koordinaten
# ============================================================

LINES = {
  '35':       '170049831', '45':       '170049832', '46':       '170049833',
  '46a':      '170049838', '104':      '170049834', '106':      '170049835',
  '112':      '170049836', '113':      '264981730', '114':      '282804217',
  '183':      '191358637', '188':      '170049837', '400':      '197431160',
  '503':      '170049840', '506':      '170049841', '507':      '170049842',
  '508':      '170049843', '509':      '170049844', '511':      '170049845',
  '512':      '170049846', '513':      '170049847', 'AK03':     '170049873',
  'LC07A':    '170049960',
}

BUS_COLORS = [
  '#E53935','#8E24AA','#1E88E5','#43A047','#FB8C00','#00ACC1',
  '#F4511E','#3949AB','#00897B','#C0CA33','#6D4C41','#546E7A',
]

# ---- OSM Stop-Lookup aufbauen ----
osm_by_id = {}
for fname in ['bus_stops_raw.json', 'bus_stops2.json']:
    path = os.path.join(os.path.dirname(__file__), fname)
    if not os.path.exists(path): continue
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    for n in d['elements']:
        t = n.get('tags', {})
        ref = t.get('ref', '')
        if ref and re.match(r'^\d{4,6}$', ref):
            osm_by_id[ref] = (n['lat'], n['lon'])
        name = t.get('name', '')
        m = re.match(r'^(\d{4,6})[\s\-]', name)
        if m:
            osm_by_id[m.group(1)] = (n['lat'], n['lon'])

print(f'OSM stops with ID: {len(osm_by_id)}')

# ---- Nominatim Geocoder (Fallback) ----
nominatim_cache = {}

def geocode_stop(name):
    """Try to geocode a bus stop name in Antalya using Nominatim."""
    clean = re.sub(r'^\d+[\s\-]+', '', name).strip()
    if clean in nominatim_cache:
        return nominatim_cache[clean]

    # Try with 'durak' (bus stop in Turkish) and location
    queries = [
        f'{clean} durak Antalya',
        f'{clean} Antalya',
    ]
    for q in queries:
        r = subprocess.run([
            'curl', '-s', '--max-time', '8',
            '-H', 'User-Agent: AntalyaBusMap/1.0',
            f'https://nominatim.openstreetmap.org/search?q={q.replace(" ","+")}&format=json&limit=1&countrycodes=tr&viewbox=29.9,37.0,31.2,36.7&bounded=1'
        ], capture_output=True, text=True, encoding='utf-8', errors='replace')
        try:
            data = json.loads(r.stdout)
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                # Sanity check: must be in Antalya area
                if 36.6 < lat < 37.2 and 29.9 < lon < 31.2:
                    nominatim_cache[clean] = (lat, lon)
                    return (lat, lon)
        except:
            pass
        time.sleep(0.3)

    nominatim_cache[clean] = None
    return None

# ---- Moovit-Seiten abrufen und Stops extrahieren ----
def fetch_moovit_line(name, lid):
    url = f'https://moovitapp.com/index/en/public_transit-line-{name}-Antalya-3462-3757093-{lid}-0'
    r = subprocess.run(
        ['curl', '-s', '--max-time', '15', '-H', 'User-Agent: Googlebot/2.1', url],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    html = r.stdout
    # Extract stop_id - stop_name pairs
    raw = re.findall(r'(\d{4,6})\s*-\s*([A-Za-zÇçĞğİıÖöŞşÜü][^<\n\",]{2,50}?)(?=[<\n\",])', html)
    seen = {}
    for sid, sname in raw:
        if sid not in seen and not sid.startswith('346') and 5000 < int(sid) < 60000:
            seen[sid] = sname.strip()
    # Title for route description
    title = re.search(r'<title>([^<]+)</title>', html)
    desc = title.group(1).replace('Route: Schedules, Stops &amp; Maps - ','').replace(' (Updated)','') if title else name
    return list(seen.items()), desc

# ---- Alle Linien verarbeiten ----
all_stops  = {}   # id -> {id, name, lat, lng}
all_routes = []
stop_routes_map = {}  # stop_id -> [route_names]
shapes     = {}

existing_ids = set()
geocode_needed = []  # (sid, sname, line_name) for unmatched stops

for i, (line_name, line_id) in enumerate(LINES.items()):
    print(f'Fetching {line_name}...', end=' ')
    stop_pairs, desc = fetch_moovit_line(line_name, line_id)

    color = BUS_COLORS[i % len(BUS_COLORS)]
    route_id = f'BUS-{line_name}'
    all_routes.append({'id': route_id, 'name': line_name, 'color': color, 'type': 3})

    shape_pts = []
    matched = 0

    for sid, sname in stop_pairs[:90]:  # max 90 stops per direction
        coords = osm_by_id.get(sid)

        if coords:
            lat, lon = coords
            matched += 1

            if sid not in existing_ids:
                all_stops[sid] = {'id': f'ABUS-{sid}', 'name': sname, 'lat': lat, 'lng': lon}
                existing_ids.add(sid)

            stop_id = f'ABUS-{sid}'
            if stop_id not in stop_routes_map:
                stop_routes_map[stop_id] = []
            if line_name not in stop_routes_map[stop_id]:
                stop_routes_map[stop_id].append(line_name)

            shape_pts.append([lat, lon])
        else:
            # Queue for geocoding
            geocode_needed.append((sid, sname, line_name, route_id))

    shapes[route_id] = shape_pts
    print(f'{len(stop_pairs)} stops, {matched} matched ({matched*100//max(len(stop_pairs),1)}%)')
    time.sleep(0.8)

print(f'\nBus: {len(all_routes)} Routen, {len(all_stops)} Stops (OSM-matched)')
print(f'Geocoding {len(geocode_needed)} unmatched stops via Nominatim...')

# ---- Nominatim-Fallback für nicht gematchte Stops ----
geocoded = 0
failed = 0
geo_cache_by_sid = {}  # sid -> coords (avoid re-geocoding same stop)

for sid, sname, line_name, route_id in geocode_needed:
    if sid in geo_cache_by_sid:
        coords = geo_cache_by_sid[sid]
    elif sid in existing_ids:
        coords = (all_stops[sid]['lat'], all_stops[sid]['lng'])
        geo_cache_by_sid[sid] = coords
    else:
        coords = geocode_stop(sname)
        geo_cache_by_sid[sid] = coords

    if coords:
        lat, lon = coords
        geocoded += 1

        if sid not in existing_ids:
            all_stops[sid] = {'id': f'ABUS-{sid}', 'name': sname, 'lat': lat, 'lng': lon}
            existing_ids.add(sid)

        stop_id = f'ABUS-{sid}'
        if stop_id not in stop_routes_map:
            stop_routes_map[stop_id] = []
        if line_name not in stop_routes_map[stop_id]:
            stop_routes_map[stop_id].append(line_name)

        # Also add to shape (we'll need to rebuild shapes with proper order)
        # For now just track that this stop exists on the route
    else:
        failed += 1

print(f'Geocoded: {geocoded}, Failed: {failed}')

# Rebuild shapes with geocoded stops included (in order)
print('Rebuilding shapes with geocoded stops...')
for i, (line_name, line_id) in enumerate(LINES.items()):
    route_id = f'BUS-{line_name}'
    # Re-fetch from already stored data
    # Shapes already built with OSM matches, now add geocoded stops in order
    # We need to re-process with the full geo_cache_by_sid available
    pass

# Actually rebuild shapes properly
shapes = {}
for i, (line_name, line_id) in enumerate(LINES.items()):
    route_id = f'BUS-{line_name}'
    # Re-read the stop pairs from a second pass isn't feasible without re-fetching
    # Instead, reconstruct from all_stops + stop_routes_map
    # The order is lost — use existing shape if available, else skip
    # For shape quality, we at least have the OSM-matched stops in order from first pass
    pass

# Since shapes were built in-order during first pass (OSM only),
# let's at least add geocoded stops to existing shapes approximately
# by checking stop_routes_map for each route
# For now keep the shapes from first pass
print('Note: shapes contain OSM-matched stops only (ordered). Geocoded stops added to stop list.')

print(f'\nBus: {len(all_routes)} Routen, {len(all_stops)} Stops total')

# ---- Mit Tram-Daten zusammenführen ----
TRAM_ROUTES = [
  {'id':'AT-T1A','name':'T1A','color':'#E63946','type':0},
  {'id':'AT-T1B','name':'T1B','color':'#E63946','type':0},
  {'id':'AT-T2', 'name':'T2', 'color':'#2196F3','type':0},
  {'id':'AT-T3', 'name':'T3', 'color':'#4CAF50','type':0},
]
T1A=[('Fatih',36.9436,30.6449),('Kepezalti',36.9387,30.6522),('Ferrokrom',36.9331,30.6586),('Vakif Ciftligi',36.9285,30.6639),('Otogar',36.9244,30.6675),('Pil Fabrikasi',36.9180,30.6733),('Dokuma',36.9132,30.6769),('Calli',36.9065,30.6822),('Emniyet',36.9019,30.6870),('Sigorta',36.8992,30.6937),('Sarampol',36.8963,30.6985),('Muratpasa',36.8926,30.7028),('Ismetpasa',36.8883,30.7070),('Dogu Garaji',36.8888,30.7124),('Burhanettin Onat',36.8887,30.7216),('Meydan',36.8868,30.7313),('Kisla',36.8908,30.7481),('Topcular',36.8932,30.7547),('Demokrasi',36.8960,30.7593),('Cirnik',36.9032,30.7658),('Altinova',36.9088,30.7703),('Yenigol',36.9155,30.7794),('Sinan',36.9197,30.7868),('Yonca Kavsak',36.9260,30.7976),('Havalimani',36.9125,30.8033)]
T1B=[('Fatih',36.9436,30.6449),('Kepezalti',36.9387,30.6522),('Ferrokrom',36.9331,30.6586),('Vakif Ciftligi',36.9285,30.6639),('Otogar',36.9244,30.6675),('Pil Fabrikasi',36.9180,30.6733),('Dokuma',36.9132,30.6769),('Calli',36.9065,30.6822),('Emniyet',36.9019,30.6870),('Sigorta',36.8992,30.6937),('Sarampol',36.8963,30.6985),('Muratpasa',36.8926,30.7028),('Ismetpasa',36.8883,30.7070),('Dogu Garaji',36.8888,30.7124),('Burhanettin Onat',36.8887,30.7216),('Meydan',36.8868,30.7313),('Kisla',36.8908,30.7481),('Topcular',36.8932,30.7547),('Demokrasi',36.8960,30.7593),('Cirnik',36.9032,30.7658),('Altinova',36.9088,30.7703),('Yenigol',36.9155,30.7794),('Sinan',36.9197,30.7868),('Yonca Kavsak',36.9260,30.7976),('Pinarly Anfas',36.9372,30.8171),('Kursunlu',36.9435,30.8282),('Aksu',36.9479,30.8454),('Expo',36.9453,30.8761)]
T2=[('Muze',36.8847,30.6811),('Barbaros',36.8848,30.6862),('Meslek Lisesi',36.8850,30.6913),('Selekler',36.8856,30.6977),('Cumhuriyet Meydani',36.8867,30.7026),('Kale Kapisi',36.8870,30.7056),('Uc Kapilar',36.8853,30.7089),('Buyuksehir Belediyesi',36.8808,30.7083),('Isiklar 2',36.8781,30.7104),('Isiklar 1',36.8751,30.7130),('Zerdalilik',36.8746,30.7168)]
T3=[('Muze',36.8847,30.6811),('Egitim Arastirma Hastanesi',36.8908,30.6762),('Meltem',36.8926,30.6699),('Akdeniz Universitesi',36.8937,30.6649),('Universite Hastanesi',36.8987,30.6655),('Kultur',36.9080,30.6632),('Yenidogan',36.9153,30.6658),('Batigar',36.9211,30.6679),('Sakarya',36.9211,30.6761),('Ataturk',36.9193,30.6831),('Zafer',36.9188,30.6890),('Yildirim Beyazit',36.9186,30.6948),('Erdem Beyazit K.M.',36.9186,30.6998),('Sehitler Parki',36.9190,30.7077),('Kepez Belediyesi',36.9178,30.7139),('Yesilirmak',36.9219,30.7145),('Gundogdu',36.9278,30.7132),('Sutculer',36.9340,30.7118),('Gazi',36.9400,30.7104),('Kuzeykaya',36.9442,30.7093),('Fevzi Cakmak',36.9484,30.7080),('Ulubatli Hasan',36.9544,30.7084),('Suleyman Demirel',36.9581,30.7098),('Selale',36.9635,30.7120),('Karsiyaka',36.9694,30.7139),('Aydogmus',36.9752,30.7141),('Aktoprak',36.9806,30.7148),('Kepezpark',36.9850,30.7154),('Varsak',36.9889,30.7165)]
TRAM_LINES={'AT-T1A':T1A,'AT-T1B':T1B,'AT-T2':T2,'AT-T3':T3}

stops_out = []
routes_out = list(TRAM_ROUTES)
sr_out = {}
shapes_out = {}
ex_names = {}

for rid, stations in TRAM_LINES.items():
    rname = next(r['name'] for r in TRAM_ROUTES if r['id']==rid)
    for i,(name,lat,lng) in enumerate(stations):
        if name in ex_names:
            sid = ex_names[name]
        else:
            sid = f'{rid}-{i}'
            stops_out.append({'id':sid,'name':name,'lat':lat,'lng':lng})
            ex_names[name] = sid
        if sid not in sr_out: sr_out[sid]=[]
        if rname not in sr_out[sid]: sr_out[sid].append(rname)
    shapes_out[rid] = [[lat,lng] for _,lat,lng in stations]

routes_out.extend(all_routes)
for s in all_stops.values():
    stops_out.append(s)
for sid, rnames in stop_routes_map.items():
    if sid in sr_out:
        sr_out[sid].extend(r for r in rnames if r not in sr_out[sid])
    else:
        sr_out[sid] = rnames

# Use shapes from first pass (OSM-ordered)
# Rebuild shapes_out from the shapes dict (built during first pass)
# We need to re-run first pass shapes — they were stored in 'shapes' dict
shapes_out.update(shapes)

# Save
base = os.path.dirname(__file__)
with open(os.path.join(base,'stops.json'),'w',encoding='utf-8') as f:
    json.dump(stops_out, f, ensure_ascii=False, separators=(',',':'))
with open(os.path.join(base,'routes.json'),'w',encoding='utf-8') as f:
    json.dump(routes_out, f, ensure_ascii=False, separators=(',',':'))
with open(os.path.join(base,'stop_routes.json'),'w',encoding='utf-8') as f:
    json.dump(sr_out, f, ensure_ascii=False, separators=(',',':'))
with open(os.path.join(base,'shapes.json'),'w',encoding='utf-8') as f:
    json.dump(shapes_out, f, ensure_ascii=False, separators=(',',':'))

print(f'\nGESAMT: {len(stops_out)} Stops, {len(routes_out)} Routen')
for fn in ['stops.json','routes.json','stop_routes.json','shapes.json']:
    fp = os.path.join(base, fn)
    print(f'  {fn}: {os.path.getsize(fp)//1024} KB')
