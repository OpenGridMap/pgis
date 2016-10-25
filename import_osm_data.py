from imposm.parser import OSMParser
import psycopg2
import json
import sys
from importers.helpers.point_helper import PointHelper
from importers.helpers.temp_point_helper import TempPointHelper

'''
WARNING: This could be a very memory intense script. The variables can grow
huge depending on the size of imports. You are adviced to import in smaller
sizes. We advice you run this with on the +.pbf+ files that were filtered to
have only the data that interests us.
Use the script - `importers/filters/power_nodes_and_ways` to filter the OSM
data files to contain only data required for this script.

NOTE: This script only imports ways and nodes. For relations import, use the
dedicated relations import script
'''

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")

pointHelper = PointHelper(cur)
tempPointHelper = TempPointHelper(cur)

class PointImporter(object):

    def perform(self, coords):
        for osmid, lon, lat in coords:
            print ".",
            tempPointHelper.insert_with_values(lat, lon, osmid)

class PowerStationImporter(object):

    def perform(self, nodes):
        for osmid, tags, coords in nodes:
            if ('power' in tags) or ('power' in tags.values()):
                # Insert the point to actual points table.
                print ".",
                pointHelper.insert_with_values(coords[1], coords[0], osmid, tags)

class PowerlineImporter(object):

    def perform(self, ways):
        for osmid, tags, refs in ways:
            if ('power' in tags) or ('power' in tags.values()):
                nodes = []
                flag = False
                for ref in refs:
                    node = pointHelper.find_with_osmid(str(ref))

                    if node is None:
                        # if couldn't find in point table. Find in temp_point
                        #   table, move that to point table.
                        node = tempPointHelper.find_with_osmid(str(ref))

                    if node is None:
                        flag = True
                    else:
                        nodes.append(node)

                if flag:
                    print("\nOne or more Points missing for line %s" % str(osmid))
                    continue

                if len(nodes) < 2:
                    print("\nLess than 2 points for line, skipping %s" % str(osmid))
                    continue

                linestring = ""
                for node in nodes:
                    linestring += "{} {},".format(node[0], node[1])
                linestring = linestring[:-1]
                print ".",
                # insert only if not already in the powerlines.
                query = '''
                    INSERT INTO powerline(geom, properties)
                    SELECT %s, %s
                    WHERE NOT EXISTS (
                        SELECT id FROM powerline WHERE geom = %s
                    )
                '''
                cur.execute(query, [
                    'LINESTRING({})'.format(linestring),
                    json.dumps({ "tags": tags, "refs": refs, "osmid": str(osmid) }),
                    'LINESTRING({})'.format(linestring),
                ])


all_points_importer = PointImporter() # temp points
power_station_importer = PowerStationImporter()
powerline_importer = PowerlineImporter()

print("\nImporting the Points to temp_points: ")
p = OSMParser(concurrency=4, coords_callback=all_points_importer.perform )
p.parse(sys.argv[1])
conn.commit()

print("\nImporting the Points (with power tag) to point: ")
p = OSMParser(concurrency=4, nodes_callback=power_station_importer.perform )
p.parse(sys.argv[1])
conn.commit()

print("\nImporting Powerlines (with power tag) to powerline: ")
p = OSMParser(concurrency=4, ways_callback=powerline_importer.perform )
p.parse(sys.argv[1])
conn.commit()

print("\nTruncating temp_points table")
tempPointHelper.truncate_table()
conn.commit()
