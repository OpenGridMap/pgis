from imposm.parser import OSMParser
import psycopg2
import json
import sys

try:
    conn = psycopg2.connect("dbname='temp_gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print "I am unable to connect to the database"


cur.execute("CREATE TEMP TABLE points ( osmid VARCHAR(80), geom GEOMETRY('POINT') ) ON COMMIT DROP");

class TempPointsImporter(object):

    def perform(self, nodes):
        for osmid, tags, coords in nodes:
            if 'power' in tags:
                query = "INSERT INTO points(osmid, geom) VALUES(%s, %s)"
                cur.execute(query, (osmid, "POINT({} {})".format(coords[1], coords[0]) )) 



temp_points_importer = TempPointsImporter()
p = OSMParser(concurrency=4, nodes_callback=temp_points_importer.perform)
p.parse(sys.argv[1])

print("Finished importing to Temp table")

class PowerStationImporter(object):

    counter = 1

    def perform(self, nodes):
        for osmid, tags, coords in nodes:
            if 'power' in tags:
                query = "INSERT INTO point(\"name\", geom, properties) VALUES(%s, %s, %s)"
                cur.execute(query, ("Point #{}".format(self.counter), "POINT({} {})".format(coords[1], coords[0]), json.dumps({ 'tags' : tags }) )) 
                self.counter += 1

class PowerlineImporter(object):

    def perform(self, ways):
        for osmid, tags, refs in ways:
            if 'power' in tags:
                nodes = []
                flag = False
                for ref in refs:
                    query = "SELECT osmid, ST_X(geom), ST_Y(geom) FROM points WHERE osmid = %s"
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
                    linestring += "{} {},".format(node[1], node[2])
                linestring = linestring[:-1]
                query = "INSERT INTO powerline(geom, properties) VALUES(%s, %s)"
                cur.execute(query, ['LINESTRING({})'.format(linestring), json.dumps({ "tags": tags, "refs": refs }) ]) 
            

power_station_importer = PowerStationImporter()
powerline_importer = PowerlineImporter()
p = OSMParser(concurrency=4, ways_callback=powerline_importer.perform )
p.parse(sys.argv[1])
conn.commit()
