from shapely.geometry import Polygon
from typing import List

class OsmMeta:
    def __init__(self, osm_id, osm_type, osm_version):
        self.osm_id = osm_id
        self.osm_type = osm_type
        self.osm_version = osm_version

    osm_id: int
    osm_type: str
    osm_version: int

class Address:
    def __init__(self, free, locality, region, postcode, country):
        self.free = free
        self.locality = locality
        self.region = region
        self.postcode = postcode
        self.country = country

    free: str
    locality: str
    region: str
    postcode: str
    country: str

class Building:
    def __init__(self, osm_meta, address, geometry):
        self.osm_meta = osm_meta
        self.address = address
        self.geometry = geometry

    def __hash__(self):
        return hash((self.osm_meta, self.geometry.wkb))

    def __eq__(self, other):
        return (self.osm_meta, self.geometry.wkb) == (other.osm_meta, other.geometry.wkb)

    osm_meta: OsmMeta
    address: Address
    geometry: Polygon

class Room:
    def __init__(self, osm_meta, geometry, level, name, ref, building):
        self.osm_meta = osm_meta
        self.geometry = geometry
        self.level = level
        self.name = name
        self.ref = ref
        self.building = building

    osm_meta: OsmMeta
    geometry: Polygon
    level: int
    name: str
    ref: str
    building: Building

class ParsedData:
    def __init__(self, buildings, rooms):
        self.buildings = buildings
        self.rooms = rooms

    buildings: List[Building]
    rooms: List[Room]