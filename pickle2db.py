import sys, pickle
import psycopg2
from psycopg2.extras import execute_values
from parser_types import *
from secrets import ANDIN_MIGRATE_PASS
from typing import List, Tuple, Dict

def pickle_load(file: str):
    with open(file, 'rb') as f:
        data: ParsedData = pickle.load(f)
        return data

def insert_import(cur, name):
    cur.execute("""
    INSERT INTO import (date, script)
        VALUES
            (NOW(), %s)
        RETURNING id;
    """, (name, ))
    import_id = cur.fetchone()[0]
    print(f'Inserted import {import_id}')
    return import_id

def insert_osm_metas(cur, osm_meta: List[OsmMeta]):
    vals = [(m.osm_id, m.osm_type, m.osm_version) for m in osm_meta]
    execute_values(cur, """
    INSERT INTO osm_element (osm_id, osm_type, osm_version)
        VALUES
            %s
        RETURNING id;
    """, vals)
    osm_element_ids = cur.fetchall()
    print(f'Inserted {len(osm_element_ids)} osm_element rows')
    return osm_element_ids

def insert_data_sources(cur, osm_element_ids: List[int], import_id: int):
    vals = [(osm_element_id, import_id) for osm_element_id in osm_element_ids]
    execute_values(cur, """
    INSERT INTO data_source (osm, import)
        VALUES
            %s
        RETURNING id;
    """, vals)
    data_source_ids = cur.fetchall()
    print(f'Inserted {len(data_source_ids)} data_source rows')
    return data_source_ids

def insert_buildings_db(cur, buildings_with_fks: List[Tuple[Building, Tuple[int, int]]]):
    buildings_with_fks = list(buildings_with_fks)
    vals = [(b.geometry.wkb, d, a) for b, (d, a) in buildings_with_fks]
    execute_values(cur, """
    INSERT INTO building (geometry, data_source, address)
        VALUES
            %s
        RETURNING id;
    """, vals, template="(ST_GeomFromWKB(%s), %s, %s)")
    building_ids = cur.fetchall()
    print(f'Inserted {len(building_ids)} building rows')
    return building_ids

def insert_building_addresses(cur, buildings: List[Building]):
    with_address = [b for b in buildings if b.address is not None]
    vals = [(b.address.free, b.address.locality, b.address.region, b.address.postcode, b.address.country) for b in with_address]
    execute_values(cur, """
    INSERT INTO address (free, locality, region, postcode, country)
        VALUES
            %s
        RETURNING id;
    """, vals)
    with_address_ids = dict(zip(with_address, cur.fetchall()))
    address_ids = [with_address_ids.get(b) for b in buildings]
    print(f'Inserted {len(address_ids)} building rows')
    return address_ids

def insert_buildings(cur, buildings: List[Building], import_id: int):
    metas = [b.osm_meta for b in buildings]
    osm_element_ids = insert_osm_metas(cur, metas)
    data_source_ids = insert_data_sources(cur, osm_element_ids, import_id)
    address_ids = insert_building_addresses(cur, buildings)
    zipped = zip(buildings, zip(data_source_ids, address_ids))
    building_ids = insert_buildings_db(cur, zipped)
    building_ids_dict = dict(zip(buildings, building_ids))
    return building_ids_dict

def insert_data_source_rooms(cur, room_data_source_list: List[Tuple[Room, int]], building_ids: Dict[Building, int]):
    vals = [(r.geometry.wkb, r.level, r.name, r.ref, building_ids[r.building], d) for r, d in room_data_source_list]
    execute_values(cur, """
    INSERT INTO room (geometry, level, name, ref, building, data_source)
        VALUES
            %s
        RETURNING id;
    """, vals, template="(ST_GeomFromWKB(%s), %s, %s, %s, %s, %s)")
    room_ids = cur.fetchall()
    print(f'Inserted {len(room_ids)} room rows')
    return room_ids

def insert_rooms(cur, rooms: List[Room], building_ids: Dict[Building, int], import_id: int):
    metas = [b.osm_meta for b in rooms]
    osm_element_ids = insert_osm_metas(cur, metas)
    data_source_ids = insert_data_sources(cur, osm_element_ids, import_id)
    room_ids = dict(zip(rooms, insert_data_source_rooms(cur, zip(rooms, data_source_ids), building_ids)))
    return room_ids


if __name__ == "__main__":
    data = pickle_load(sys.argv[1])
    conn = psycopg2.connect(host="localhost", database="andin_dev", user="andin_migrate", password=ANDIN_MIGRATE_PASS)
    cur = conn.cursor()
    import_id = insert_import(cur, 'osm')
    building_ids = insert_buildings(cur, data.buildings, import_id)
    room_ids = insert_rooms(cur, data.rooms, building_ids, import_id)
    conn.commit()
    cur.close()
    conn.close()