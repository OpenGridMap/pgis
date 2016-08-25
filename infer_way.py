import psycopg2
import json
import sys
import ast

try:
    conn = psycopg2.connect("dbname='gis' user='Munna' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")

nodes_osmids = (
'3212196101', '3212196097', '3212196093', '3212196089', '3212196086', '3212196083',
'3212196077', '3212196075', '3212196071', '3212196045', '3212196012', '3212195977',
'3212195974', '3212195967', '3212195960', '3212195952', '3212195947',
'3212195940', '3212195935', '3212195931', '3212195926', '3212195925',
'3212195924', '3212195923', '3212195917', '3212195908', '3212195898',
'3212195884', '3212195874', '3212195866', '3212195869', '3212195878',
'3212195882', '3212195889', '3212195895', '3212195893', '3212195896'
)

nodes_query = "SELECT id, geom, properties->>'osmid' FROM point "\
    "WHERE properties->>'osmid' in %s"
cur.execute(nodes_query, (nodes_osmids, ))

nodes = cur.fetchall()

print(len(nodes_osmids))
print(len(nodes))


processing_node = "3212196097"
processed_nodes = []
processed_nodes.append(processing_node)

is_complete = False

while is_complete == False:
    # print(processed_nodes)
    # print "processing - ",
    # print(processing_node)
    fetch_closest_query = '''
        WITH current_point AS (
            SELECT id, ST_AsText(geom) AS geom FROM point WHERE (properties->>'osmid') = %s
        )
        SELECT point.id, point.properties->>'osmid' FROM point, current_point
            WHERE ST_Distance(ST_GeomFromText(current_point.geom), point.geom) > 0.002
                AND ST_Distance(ST_GeomFromText(current_point.geom), point.geom) < 0.09
                AND properties->>'osmid' IN %s
            ORDER BY ST_Distance(ST_GeomFromText(current_point.geom), point.geom) ASC
            LIMIT 1'''
    cur.execute(fetch_closest_query, [
        processing_node,
        tuple(set(tuple(processed_nodes)) ^ set(nodes_osmids))
    ])
    closest_node = cur.fetchone()
    if closest_node is not None and len(closest_node) > 0:
        print "Closest is - ",
        print(closest_node[1])
        processing_node = closest_node[1]
        processed_nodes.append(processing_node)
    else:
        print("\n*********** IS COMPLETE **************\n")
        is_complete = True

print(processed_nodes)
