from typing import List
from shapely.geometry import Polygon
import sys, json, pickle
from parser_types import *
import nominatim

def json_load(file: str):
    with open(file, 'r') as f:
        return json.load(f)

def picle_dump(data, file: str):
    with open('out.bin', 'wb') as f:
        pickle.dump(data, f)

def get_coords(node: int, nodelib: List[dict]):
    try:
        matching = next(n for n in nodelib if n["id"] == node)
    except StopIteration:
        raise(Exception('No matching node found, overpass data might be corrupt'))
    
    return (matching["lon"], matching["lat"])

def get_containing_building(geometry: Polygon, buildinglib: List[Building]):
    try:
        matching = next(b for b in buildinglib if fuzzy_contains(b.geometry, geometry))
    except StopIteration:
        raise(Exception('No containing building found, might be a loose room'))
    
    return matching

def fuzzy_contains(a: Polygon, b: Polygon):
    area = b.area
    areaIntersecting = a.intersection(b).area
    return (areaIntersecting / area) > 0.99

def extract_osm_elements(raw):
    els = raw["elements"]
    ways = [el for el in els if el["type"] == "way"]
    nodes = [el for el in els if el["type"] == "node"]
    tagged_way = [el for el in ways if "tags" in el]
    osm_buildings = [el for el in tagged_way if "building" in el["tags"]]
    osm_rooms = [el for el in tagged_way if "indoor" in el["tags"]]
    return (osm_buildings, osm_rooms, nodes)

def parse_osm_building(room: object, nodeLib: List[dict]):
    if room["type"] != "way":
        raise(NotImplementedError('support for non-way buildings'))
    meta = OsmMeta(room["id"], room["type"], room["version"])
    points = [get_coords(node, nodeLib) for node in room["nodes"]]
    geometry = Polygon(points)
    address = Address(None, None, None, None, None)
    return Building(meta, address, geometry)

def parse_osm_room(room: object, nodeLib: List[dict], buildinglib: List[Building]):
    if room["type"] != "way":
        raise(NotImplementedError('support for non-way rooms'))
    
    tags = room["tags"]
    if tags["indoor"] != "room":
        raise(NotImplementedError('support for non-room indoor elements (like stairwells)'))
    try:
        level = int(tags["level"]) if "level" in tags else 0
    except ValueError:
        raise(NotImplementedError('support for non-room indoor elements (like stairwells)'))
    name = tags["name"].strip() if "name" in tags else None
    ref = tags["ref"].strip() if "ref" in tags else None

    meta = OsmMeta(room["id"], room["type"], room["version"])
    points = [get_coords(node, nodeLib) for node in room["nodes"]]
    geometry = Polygon(points)
    building = get_containing_building(geometry, buildinglib)
    return Room(meta, geometry, level, name, ref, building)

def parse(osm_buildings, osm_rooms, nodes):
    buildings = []
    for osm_building in osm_buildings:
        buildings.append(parse_osm_building(osm_building, nodes))

    rooms = []
    for osm_room in osm_rooms:
        try:
            rooms.append(parse_osm_room(osm_room, nodes, buildings))
        except NotImplementedError:
            continue # Skip
    
    return ParsedData(buildings, rooms)

def gen_zero():
    while True:
        yield 0

def only_used_buildings(buildings: List[Building], rooms: List[Room]):
    no_refs = dict(zip(buildings, gen_zero()))
    for room in rooms:
        no_refs[room.building] += 1
    used_buildings = [b for b, refs in no_refs.items() if refs > 0]
    return used_buildings

def lookup_building_addresses(buildings: List[Building]):
    metas = [b.osm_meta for b in buildings]
    addresses = nominatim.lookup(metas)
    for i, building in enumerate(buildings):
        building.address = addresses[i]


if __name__ == "__main__":
    overpass_data = json_load(sys.argv[1])
    osm_buildings, osm_rooms, nodes = extract_osm_elements(overpass_data)
    parsed = parse(osm_buildings, osm_rooms, nodes)
    parsed.buildings = only_used_buildings(parsed.buildings, parsed.rooms)
    lookup_building_addresses(parsed.buildings)
    picle_dump(parsed, sys.argv[2])
