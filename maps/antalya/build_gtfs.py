import json, os

# ============================================================
# Antalya - Tram + Bus aus OpenStreetMap
# ============================================================

# ---------- TRAM ----------
TRAM_ROUTES = [
  {'id':'AT-T1A','name':'T1A','color':'#E63946','type':0},
  {'id':'AT-T1B','name':'T1B','color':'#E63946','type':0},
  {'id':'AT-T2', 'name':'T2', 'color':'#2196F3','type':0},
  {'id':'AT-T3', 'name':'T3', 'color':'#4CAF50','type':0},
]

T1A = [
  ('Fatih',             36.9436, 30.6449),
  ('Kepezalti',         36.9387, 30.6522),
  ('Ferrokrom',         36.9331, 30.6586),
  ('Vakif Ciftligi',    36.9285, 30.6639),
  ('Otogar',            36.9244, 30.6675),
  ('Pil Fabrikasi',     36.9180, 30.6733),
  ('Dokuma',            36.9132, 30.6769),
  ('Calli',             36.9065, 30.6822),
  ('Emniyet',           36.9019, 30.6870),
  ('Sigorta',           36.8992, 30.6937),
  ('Sarampol',          36.8963, 30.6985),
  ('Muratpasa',         36.8926, 30.7028),
  ('Ismetpasa',         36.8883, 30.7070),
  ('Dogu Garaji',       36.8888, 30.7124),
  ('Burhanettin Onat',  36.8887, 30.7216),
  ('Meydan',            36.8868, 30.7313),
  ('Kisla',             36.8908, 30.7481),
  ('Topcular',          36.8932, 30.7547),
  ('Demokrasi',         36.8960, 30.7593),
  ('Cirnik',            36.9032, 30.7658),
  ('Altinova',          36.9088, 30.7703),
  ('Yenigol',           36.9155, 30.7794),
  ('Sinan',             36.9197, 30.7868),
  ('Yonca Kavsak',      36.9260, 30.7976),
  ('Havalimani',        36.9125, 30.8033),
]
T1B = [
  ('Fatih',             36.9436, 30.6449),
  ('Kepezalti',         36.9387, 30.6522),
  ('Ferrokrom',         36.9331, 30.6586),
  ('Vakif Ciftligi',    36.9285, 30.6639),
  ('Otogar',            36.9244, 30.6675),
  ('Pil Fabrikasi',     36.9180, 30.6733),
  ('Dokuma',            36.9132, 30.6769),
  ('Calli',             36.9065, 30.6822),
  ('Emniyet',           36.9019, 30.6870),
  ('Sigorta',           36.8992, 30.6937),
  ('Sarampol',          36.8963, 30.6985),
  ('Muratpasa',         36.8926, 30.7028),
  ('Ismetpasa',         36.8883, 30.7070),
  ('Dogu Garaji',       36.8888, 30.7124),
  ('Burhanettin Onat',  36.8887, 30.7216),
  ('Meydan',            36.8868, 30.7313),
  ('Kisla',             36.8908, 30.7481),
  ('Topcular',          36.8932, 30.7547),
  ('Demokrasi',         36.8960, 30.7593),
  ('Cirnik',            36.9032, 30.7658),
  ('Altinova',          36.9088, 30.7703),
  ('Yenigol',           36.9155, 30.7794),
  ('Sinan',             36.9197, 30.7868),
  ('Yonca Kavsak',      36.9260, 30.7976),
  ('Pinarly Anfas',     36.9372, 30.8171),
  ('Kursunlu',          36.9435, 30.8282),
  ('Aksu',              36.9479, 30.8454),
  ('Expo',              36.9453, 30.8761),
]
T2 = [
  ('Muze',              36.8847, 30.6811),
  ('Barbaros',          36.8848, 30.6862),
  ('Meslek Lisesi',     36.8850, 30.6913),
  ('Selekler',          36.8856, 30.6977),
  ('Cumhuriyet Meydani',36.8867, 30.7026),
  ('Kale Kapisi',       36.8870, 30.7056),
  ('Uc Kapilar',        36.8853, 30.7089),
  ('Buyuksehir Belediyesi', 36.8808, 30.7083),
  ('Isiklar 2',         36.8781, 30.7104),
  ('Isiklar 1',         36.8751, 30.7130),
  ('Zerdalilik',        36.8746, 30.7168),
]
T3 = [
  ('Muze',              36.8847, 30.6811),
  ('Egitim Arastirma Hastanesi', 36.8908, 30.6762),
  ('Meltem',            36.8926, 30.6699),
  ('Akdeniz Universitesi', 36.8937, 30.6649),
  ('Universite Hastanesi', 36.8987, 30.6655),
  ('Kultur',            36.9080, 30.6632),
  ('Yenidogan',         36.9153, 30.6658),
  ('Batigar',           36.9211, 30.6679),
  ('Sakarya',           36.9211, 30.6761),
  ('Ataturk',           36.9193, 30.6831),
  ('Zafer',             36.9188, 30.6890),
  ('Yildirim Beyazit',  36.9186, 30.6948),
  ('Erdem Beyazit K.M.',36.9186, 30.6998),
  ('Sehitler Parki',    36.9190, 30.7077),
  ('Kepez Belediyesi',  36.9178, 30.7139),
  ('Yesilirmak',        36.9219, 30.7145),
  ('Gundogdu',          36.9278, 30.7132),
  ('Sutculer',          36.9340, 30.7118),
  ('Gazi',              36.9400, 30.7104),
  ('Kuzeykaya',         36.9442, 30.7093),
  ('Fevzi Cakmak',      36.9484, 30.7080),
  ('Ulubatli Hasan',    36.9544, 30.7084),
  ('Suleyman Demirel',  36.9581, 30.7098),
  ('Selale',            36.9635, 30.7120),
  ('Karsiyaka',         36.9694, 30.7139),
  ('Aydogmus',          36.9752, 30.7141),
  ('Aktoprak',          36.9806, 30.7148),
  ('Kepezpark',         36.9850, 30.7154),
  ('Varsak',            36.9889, 30.7165),
]
TRAM_LINES = {'AT-T1A':T1A,'AT-T1B':T1B,'AT-T2':T2,'AT-T3':T3}

# ---------- BUS aus OSM ----------
with open('bus_full_raw.json', encoding='utf-8') as f:
    osm = json.load(f)

elements   = osm['elements']
osm_nodes  = {e['id']:e for e in elements if e['type']=='node'}
osm_ways   = {e['id']:e for e in elements if e['type']=='way'}
osm_rels   = [e for e in elements if e['type']=='relation']

BUS_COLORS = {
    '600':'#FF9800', 'DC15':'#9C27B0', 'VF63':'#009688',
    'HAVAS':'#F44336', '104':'#3F51B5', 'UC32':'#795548',
    'VS18':'#607D8B', 'KL08':'#E91E63',
}

bus_routes = []
bus_stops  = []
bus_stop_routes = {}
bus_shapes = {}

seen_rels = set()  # avoid duplicate directions
seen_stop_names = {}

for rel in osm_rels:
    tags = rel.get('tags', {})
    ref  = tags.get('ref', '').strip()
    name = tags.get('name', ref)
    if not ref or ref == '?': continue

    rid = f'BUS-{ref}'

    # Collect shape from ways
    if rid not in bus_shapes:
        shape_pts = []
        for m in rel.get('members', []):
            if m['type'] == 'way' and m['ref'] in osm_ways:
                way = osm_ways[m['ref']]
                for nid in way.get('nodes', []):
                    if nid in osm_nodes:
                        n = osm_nodes[nid]
                        shape_pts.append([round(n['lat'],6), round(n['lon'],6)])
        if shape_pts:
            bus_shapes[rid] = shape_pts

    # Collect stop nodes
    for m in rel.get('members', []):
        if m['type'] != 'node': continue
        if m.get('role','') not in ('stop','stop_entry_only','stop_exit_only','platform',''):
            continue
        nid = m['ref']
        if nid not in osm_nodes: continue
        n   = osm_nodes[nid]
        nt  = n.get('tags', {})
        sname = nt.get('name') or nt.get('ref') or f'Stop {nid}'

        if sname in seen_stop_names:
            sid = seen_stop_names[sname]
        else:
            sid = f'ABUS-{nid}'
            bus_stops.append({'id':sid,'name':sname,'lat':round(n['lat'],6),'lng':round(n['lon'],6)})
            seen_stop_names[sname] = sid

        if sid not in bus_stop_routes: bus_stop_routes[sid] = []
        if ref not in bus_stop_routes[sid]:
            bus_stop_routes[sid].append(ref)

    # Add route (deduplicate by ref)
    if rid not in seen_rels:
        seen_rels.add(rid)
        short_ref = ref.split(',')[0].strip()
        color = BUS_COLORS.get(short_ref, '#1E88E5')
        bus_routes.append({'id': rid, 'name': short_ref, 'color': color, 'type': 3})

print(f'Bus: {len(bus_routes)} Routen, {len(bus_stops)} Stops')

# ---------- Alles zusammenführen ----------
stops       = []
routes      = list(TRAM_ROUTES)
stop_routes = {}
shapes      = {}

existing_names = {}

# Tram-Stationen
for route_id, stations in TRAM_LINES.items():
    route_name = next(r['name'] for r in TRAM_ROUTES if r['id']==route_id)
    for i,(name,lat,lng) in enumerate(stations):
        if name in existing_names:
            sid = existing_names[name]
        else:
            sid = f'{route_id}-{i}'
            stops.append({'id':sid,'name':name,'lat':lat,'lng':lng})
            existing_names[name] = sid
        if sid not in stop_routes: stop_routes[sid] = []
        if route_name not in stop_routes[sid]: stop_routes[sid].append(route_name)
    shapes[route_id] = [[lat,lng] for _,lat,lng in stations]

# Bus-Stationen
routes.extend(bus_routes)
for s in bus_stops:
    if s['name'] not in existing_names:
        stops.append(s)
        existing_names[s['name']] = s['id']
for sid, rnames in bus_stop_routes.items():
    if sid in stop_routes:
        for r in rnames:
            if r not in stop_routes[sid]: stop_routes[sid].append(r)
    else:
        stop_routes[sid] = rnames
shapes.update(bus_shapes)

# ---------- Speichern ----------
with open('stops.json','w',encoding='utf-8') as f:
    json.dump(stops, f, ensure_ascii=False, separators=(',',':'))
with open('routes.json','w',encoding='utf-8') as f:
    json.dump(routes, f, ensure_ascii=False, separators=(',',':'))
with open('stop_routes.json','w',encoding='utf-8') as f:
    json.dump(stop_routes, f, ensure_ascii=False, separators=(',',':'))
with open('shapes.json','w',encoding='utf-8') as f:
    json.dump(shapes, f, ensure_ascii=False, separators=(',',':'))

print(f'GESAMT: {len(stops)} Stops, {len(routes)} Routen')
for fn in ['stops.json','routes.json','stop_routes.json','shapes.json']:
    print(f'  {fn}: {os.path.getsize(fn)//1024} KB')
print('FERTIG!')
