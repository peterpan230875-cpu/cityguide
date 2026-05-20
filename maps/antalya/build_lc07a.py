import json, re, subprocess, time, urllib.request, glob
import xml.etree.ElementTree as ET
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ---- Build OSM stop lookup ----
osm_by_id = {}
for fname in ['bus_stops_raw.json','bus_stops2.json']:
    try:
        with open(fname, encoding='utf-8') as f:
            d = json.load(f)
        for n in d['elements']:
            t = n.get('tags',{})
            ref = t.get('ref','')
            if ref and re.match(r'^\d{4,6}$', ref): osm_by_id[ref] = (n['lat'], n['lon'])
            name = t.get('name','')
            m = re.match(r'^(\d{4,6})[\s\-]', name)
            if m: osm_by_id[m.group(1)] = (n['lat'], n['lon'])
            if name and re.match(r'^\d{4,6}$', name): osm_by_id[name] = (n['lat'], n['lon'])
    except: pass

for fname in glob.glob('osm_*.xml'):
    try:
        with open(fname,'rb') as fh:
            if not fh.read(5).startswith(b'<?xml'): continue
        tree = ET.parse(fname)
        root = tree.getroot()
        for node in root.findall('node'):
            tags = {t.attrib['k']: t.attrib['v'] for t in node.findall('tag')}
            is_stop = (tags.get('highway')=='bus_stop' or tags.get('public_transport') in ('stop_position','platform'))
            if not is_stop: continue
            lat, lon = float(node.attrib['lat']), float(node.attrib['lon'])
            ref = tags.get('ref','').strip(); name = tags.get('name','').strip()
            if ref and re.match(r'^\d{4,6}$', ref): osm_by_id[ref] = (lat, lon)
            if name and re.match(r'^\d{4,6}$', name): osm_by_id[name] = (lat, lon)
            m2 = re.match(r'^(\d{4,6})[\s\-]', name)
            if m2: osm_by_id[m2.group(1)] = (lat, lon)
    except: pass

print(f'OSM lookup: {len(osm_by_id)} IDs')

# ---- Manual coordinates for stops not in OSM ----
MANUAL = {
    # Kundu (easternmost terminus)
    '16377': (36.8630, 30.9600),  # Kundu-22
    # Yaşar Sobutay Blv (interpolated along coastal road)
    '11221': (36.8589, 30.8939),  # -22 (between -21:30.8984 and -23:30.8893)
    '11591': (36.8582, 30.8860),  # -24
    '10848': (36.8575, 30.8828),  # -25
    '11224': (36.8569, 30.8756),  # -27
    '11226': (36.8586, 30.8634),  # -30
    '11227': (36.8592, 30.8590),  # -31
    '11228': (36.8598, 30.8547),  # -32
    '13539': (36.8604, 30.8504),  # -33
    '11589': (36.8610, 30.8460),  # -34
    '10850': (36.8598, 30.8267),  # -38 (between -37:30.8314 and -39:30.8219)
    '10853': (36.8583, 30.8168),  # -40
    '11112': (36.8570, 30.8117),  # -41
    '11852': (36.8556, 30.8066),  # -42
    # Barınaklar Blv
    '10109': (36.8544, 30.7769),  # -15
    # City center (Markantalya → Anafartalar) — anchored to OSM stops in area
    '10325': (36.8913, 30.7052),  # Hasan Subaşı Cd (anon OSM stop 11876 area)
    '10326': (36.8919, 30.6989),  # Şehit Binbaşı Cengiz Toytunç Cd-1 (anon 10364)
    '10327': (36.8896, 30.6970),  # Şehit Binbaşı Cengiz Toytunç Cd-2 (anon 10328)
    # Mehmet Akif Cd — route goes EAST from Özdilek (30.680) toward Vatan Blv (30.690)
    '14130': (36.9113, 30.6826),  # Mehmet Akif Cd-1
    '11092': (36.9120, 30.6851),  # Mehmet Akif Cd-2
    '12546': (36.9133, 30.6895),  # Mehmet Akif Cd-4 (east of confirmed -3)
    # Mustafa Pehlivanoğlu Cd — runs NORTH-SOUTH at eastern end (~lon 30.689)
    '10649': (36.9153, 30.6893),  # -2 (north leg of the rectangle)
    '11689': (36.9174, 30.6893),  # -3 (continue north)
    # Tevfik Fikret Cd — runs EAST-WEST going WEST at top of rectangle (~lat 36.919)
    '10650': (36.9186, 30.6873),  # -1 (turn west at top)
    '10651': (36.9190, 30.6845),  # -2
    '12902': (36.9193, 30.6818),  # -3
    # Namık Kemal Blv — continues northwest from top-left corner toward Otogar
    '10749': (36.9197, 30.6797),  # -3
    '10750': (36.9202, 30.6768),  # -4
    '11683': (36.9207, 30.6742),  # -5
    '11684': (36.9212, 30.6716),  # -6
    # Otogar area
    '12756': (36.9220, 30.6696),  # Dumlupınar Blv-1
    '13007': (36.9244, 30.6675),  # Otogar Depolama (confirmed)
}

# Merge manual into OSM lookup
osm_by_id.update(MANUAL)

# ---- Full LC07A stop list ----
LC07A_STOPS = [
    ('16377','Kundu-22'),('11599','Kundu-16'),('14639','Kundu-17'),('11600','Kundu-18'),
    ('11601','Kundu-19'),('11595','Yaşar Sobutay Blv-21'),('11221','Yaşar Sobutay Blv-22'),
    ('11222','Yaşar Sobutay Blv-23'),('11591','Yaşar Sobutay Blv-24'),('10848','Yaşar Sobutay Blv-25'),
    ('12613','Yaşar Sobutay Blv-26'),('11224','Yaşar Sobutay Blv-27'),('12420','Yaşar Sobutay Blv-28'),
    ('11225','Yaşar Sobutay Blv-29'),('11226','Yaşar Sobutay Blv-30'),('11227','Yaşar Sobutay Blv-31'),
    ('11228','Yaşar Sobutay Blv-32'),('13539','Yaşar Sobutay Blv-33'),('11589','Yaşar Sobutay Blv-34'),
    ('11230','Yaşar Sobutay Blv-35'),('11231','Yaşar Sobutay Blv-36'),('11232','Yaşar Sobutay Blv-37'),
    ('10850','Yaşar Sobutay Blv-38'),('11111','Yaşar Sobutay Blv-39'),('10853','Yaşar Sobutay Blv-40'),
    ('11112','Yaşar Sobutay Blv-41'),('11852','Yaşar Sobutay Blv-42'),('11113','Lara Cd-11'),
    ('10095','Lara Cd-12'),('10097','Havaalanı Cd-1'),('10099','Havaalanı Cd-2'),
    ('10101','Barınaklar Blv-11'),('10103','Barınaklar Blv-12'),('10105','Düden Parkı-2'),
    ('10107','Barınaklar Blv-14'),('10109','Barınaklar Blv-15'),('10110','Barınaklar Blv-16'),
    ('10112','Barınaklar Blv-17'),('10113','Barınaklar Blv-18'),('10114','Barınaklar Blv-19'),
    ('11810','Barınaklar Blv-20'),('10116','Muratpaşa Belediyesi'),('10118','Terracity-1'),
    ('10119','Tekelioğlu Cd-8'),('10120','Tekelioğlu Cd-9'),('10121','Tekelioğlu Cd-10'),
    ('10123','İsmet Gökşen Cd-8'),('10124','İsmet Gökşen Cd-9'),('10125','İsmet Gökşen Cd-10'),
    ('10127','İsmet Gökşen Cd-11'),('10128','İsmet Gökşen Cd-12'),('10129','İsmet Gökşen Cd-13'),
    ('10131','Metin Kasapoğlu Cd-5'),('13822','Metropol Çarşısı'),('10134','Metin Kasapoğlu Cd-7'),
    ('10135','Metin Kasapoğlu Cd-8'),('10502','Cebesoy Cd-7'),('10503','Cebesoy Cd-8'),
    ('10504','Cebesoy Cd-9'),('10505','Cebesoy Cd-10'),('10321','Cebesoy Cd-11'),
    ('10323','Cebesoy Cd-12'),('10148','Fahrettin Altay Cd'),('10324','Markantalya -2'),
    ('10325','Hasan Subaşı Cd'),('10326','Şehit Binbaşı Cengiz Toytunç Cd-1'),
    ('10327','Şehit Binbaşı Cengiz Toytunç Cd-2'),('10785','Anafartalar Cd-6'),
    ('10378','Beşşehitler Parkı'),('10545','Anafartalar Cd-8'),('10546','Atatürk Devlet Hastanesi-2'),
    ('10547','Vatan Blv-1'),('12197','Vatan Blv-2'),('10629','Özdilek Alış Veriş Merkezi-3'),
    ('14130','Mehmet Akif Cd-1'),('11092','Mehmet Akif Cd-2'),('10302','Mehmet Akif Cd-3'),
    ('12546','Mehmet Akif Cd-4'),('10649','Mustafa Pehlivanoğlu Cd-2'),('11689','Mustafa Pehlivanoğlu Cd-3'),
    ('10650','Tevfik Fikret Cd-1'),('10651','Tevfik Fikret Cd-2'),('12902','Tevfik Fikret Cd-3'),
    ('10749','Namık Kemal Blv-3'),('10750','Namık Kemal Blv-4'),('11683','Namık Kemal Blv-5'),
    ('11684','Namık Kemal Blv-6'),('12756','Dumlupınar Blv-1'),('13007','Otogar Depolama'),
]

# ---- Load existing data ----
with open('stops.json', encoding='utf-8') as f:
    stops_list = json.load(f)
with open('routes.json', encoding='utf-8') as f:
    routes_list = json.load(f)
with open('stop_routes.json', encoding='utf-8') as f:
    sr = json.load(f)
with open('shapes.json', encoding='utf-8') as f:
    shapes = json.load(f)

existing_stop_ids = {s['id'] for s in stops_list}

# ---- Add LC07A stops ----
shape_pts = []
for sid, sname in LC07A_STOPS:
    coords = osm_by_id.get(sid)
    if not coords:
        print(f'  STILL MISSING: {sid} - {sname}')
        continue
    lat, lon = coords[0], coords[1]
    stop_id = f'ABUS-{sid}'
    if stop_id not in existing_stop_ids:
        stops_list.append({'id': stop_id, 'name': sname, 'lat': lat, 'lng': lon})
        existing_stop_ids.add(stop_id)
    if stop_id not in sr:
        sr[stop_id] = []
    if 'LC07A' not in sr[stop_id]:
        sr[stop_id].append('LC07A')
    shape_pts.append([lat, lon])

print(f'LC07A: {len(shape_pts)}/89 stops with coords')

# For the SHAPE, use only OSM-confirmed stops (not manually guessed ones)
# Manual stops go into stops.json but must NOT distort the route shape
OSM_CONFIRMED = {
    '11599','14639','11600','11601','11595','11222','12613','12420','11225',
    '11230','11231','11232','11111','11113','10095','10097','10099','10101',
    '10103','10105','10107','10110','10112','10113','10114','11810','10116',
    '10118','10119','10120','10121','10123','10124','10125','10127','10128',
    '10129','10131','13822','10134','10135','10502','10503','10504','10505',
    '10321','10323','10148','10324','10785','10378','10545','10546','10547',
    '12197','10629','10302','13007',
}
shape_pts_confirmed = []
for sid, sname in LC07A_STOPS:
    if sid not in OSM_CONFIRMED: continue
    coords = osm_by_id.get(sid)
    if coords:
        shape_pts_confirmed.append([coords[0], coords[1]])
print(f'Shape uses {len(shape_pts_confirmed)} OSM-confirmed stops only')

# Add route
routes_list.append({'id': 'BUS-LC07A', 'name': 'LC07A', 'color': '#C0CA33', 'type': 3})

# ---- OSRM routing ----
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
while i < len(shape_pts_confirmed) - 1:
    chunk = shape_pts_confirmed[i:i+10]
    if len(chunk) < 2: break
    try:
        r = osrm_route_chunk(chunk)
        if r:
            routed.extend(r[1:] if routed else r)
        else:
            routed.extend(chunk)
    except Exception as e:
        print(f'  OSRM error at {i}: {e}')
        routed.extend(chunk)
    i += 9
    time.sleep(0.15)

shapes['BUS-LC07A'] = routed
print(f'  {len(shape_pts_confirmed)} confirmed stops -> {len(routed)} pts')

# ---- Save ----
with open('stops.json', 'w', encoding='utf-8') as f:
    json.dump(stops_list, f, ensure_ascii=False, separators=(',',':'))
with open('routes.json', 'w', encoding='utf-8') as f:
    json.dump(routes_list, f, ensure_ascii=False, separators=(',',':'))
with open('stop_routes.json', 'w', encoding='utf-8') as f:
    json.dump(sr, f, ensure_ascii=False, separators=(',',':'))
with open('shapes.json', 'w', encoding='utf-8') as f:
    json.dump(shapes, f, ensure_ascii=False, separators=(',',':'))

import os
print(f'\nGESAMT: {len(stops_list)} Stops, {len(routes_list)} Routen')
for fn in ['stops.json','routes.json','stop_routes.json','shapes.json']:
    print(f'  {fn}: {os.path.getsize(fn)//1024} KB')
