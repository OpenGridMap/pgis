from imposm.parser import OSMParser
import psycopg2
import json
import sys

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print "I am unable to connect to the database"

class PowerStationImporter(object):

    def perform(self, nodes):
        for osmid, tags, coords in nodes:
            if 'power' in tags:
                query = "INSERT INTO point(geom, properties, revised) VALUES(%s, %s, TRUE)"
                print("INSERTING {} {}".format(coords[1], coords[0]))
                cur.execute(query, ("POINT({} {})".format(coords[1], coords[0]), json.dumps({ 'tags' : tags , 'osmid' : osmid}) )) 

class PowerlineImporter(object):

    def perform(self, ways):
        for osmid, tags, refs in ways:
            if 'power' in tags:
                nodes = []
                flag = False
                for ref in refs:
                    query = "SELECT ST_X(geom), ST_Y(geom) FROM point WHERE properties->>'osmid' = %s"
                    cur.execute(query, [str(ref)] )
                    node = cur.fetchone()
                    if node is None:
                        flag = True
                    else:
                        nodes.append(node)
                    
                if flag:
                    break

                linestring = ""
                for node in nodes:
                    linestring += "{} {},".format(node[0], node[1])
                linestring = linestring[:-1]
                print("INSERTING {}".format(linestring))
                query = "INSERT INTO powerline(geom, properties) VALUES(%s, %s)"
                try:
                    cur.execute(query, ['LINESTRING({})'.format(linestring), json.dumps({ "tags": tags, "refs": refs }) ]) 
                except psycopg2.InternalError as e:
                    print("ERROR: {}".format(e))
            

power_station_importer = PowerStationImporter()
powerline_importer = PowerlineImporter()

p = OSMParser(concurrency=4, nodes_callback=power_station_importer.perform )
p.parse(sys.argv[1])
conn.commit()

p = OSMParser(concurrency=4, ways_callback=powerline_importer.perform )
p.parse(sys.argv[1])
conn.commit()
