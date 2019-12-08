import psycopg2
from psycopg2.extras import execute_values
from secrets import ANDIN_MIGRATE_PASS

conn = psycopg2.connect(host="localhost", database="andin_dev", user="andin_migrate", password=ANDIN_MIGRATE_PASS)
cur = conn.cursor()

cur.execute("""
INSERT INTO import (date, script)
    VALUES
        (NOW(), 'tst6r')
    RETURNING id;
""")
import_id = cur.fetchone()[0]

print(f'Inserted import {import_id}')

cur.execute("""
INSERT INTO survey (surveyor, external)
    VALUES
        ('Test Surveyor abc', False)
    RETURNING id;
""")
survey_id = cur.fetchone()[0]

print(f'Inserted survey {survey_id}')


cur.execute("""
INSERT INTO data_source (survey, import)
    VALUES
        (%s, %s)
    RETURNING id;
""", (survey_id, import_id))
data_source_id = cur.fetchone()[0]

print(f'Inserted data_source {data_source_id}')


BUILDING_GEOM = 'POLYGON ((4.728224873542786 50.846477240936466, 4.7284770011901855 50.846477240936466, 4.7284770011901855 50.84674482076022, 4.728224873542786 50.84674482076022, 4.728224873542786 50.846477240936466))'
cur.execute("""
INSERT INTO building (geometry, data_source, name)
    VALUES
        (ST_GeomFromText(%s), %s, %s)
    RETURNING id;
""", (BUILDING_GEOM, data_source_id, 'Building name'))
building_id = cur.fetchone()[0]

print(f'Inserted building {building_id}')


ROOM_GEOMS = (
    'POLYGON ((4.728278517723086 50.846631353554024, 4.728334844112399 50.846631353554024, 4.728334844112399 50.84670417582255, 4.728278517723086 50.84670417582255, 4.728278517723086 50.846631353554024))',
    'POLYGON ((4.728367030620571 50.84651957961835, 4.728426039218899 50.84651957961835, 4.728426039218899 50.846611031040176, 4.728367030620571 50.846611031040176, 4.728367030620571 50.84651957961835))',
    'POLYGON ((4.728267030620571 50.84651957961835, 4.728367030620571 50.84651957961835, 4.728367030620571 50.846611031040176, 4.728267030620571 50.846611031040176, 4.728267030620571 50.84651957961835))'
)
room_vals = [(0, geom, building_id, data_source_id) for geom in ROOM_GEOMS]
room_vals.extend([(1, geom, building_id, data_source_id) for geom in ROOM_GEOMS])
execute_values(cur, """
INSERT INTO room (level, geometry, building, data_source)
    VALUES
        %s
    RETURNING id;
""", room_vals)
room_ids = cur.fetchall()

print(f'Inserted rooms {[id for (id, ) in room_ids]}')

conn.commit()
cur.close()
conn.close()