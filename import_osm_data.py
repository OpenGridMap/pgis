from imposm.parser import OSMParser
import psycopg2
import json
import sys

try:
    conn = psycopg2.connect("dbname='osm' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
    conn2 = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur2 = conn2.cursor()
except:
    print "I am unable to connect to the database"


# class PowerStationImporter(object):

#     def perform(self, nodes):
#         for osmid, tags, coords in nodes:
#             if 'power' in tags:
#                 query = "INSERT INTO points(osmid, geom) VALUES(%s, %s)"
#                 cur.execute(query, (osmid, "POINT({} {})".format(coords[1], coords[0]) )) 

# importer = PowerStationImporter()
# p = OSMParser(concurrency=4, nodes_callback=importer.perform)
# p.parse(sys.argv[1])
# conn.commit()


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
                cur2.execute(query, ['LINESTRING({})'.format(linestring), json.dumps({ "tags": tags, "refs": refs }) ]) 
                conn2.commit()
            

importer = PowerlineImporter()
p = OSMParser(concurrency=4, ways_callback=importer.perform)
p.parse(sys.argv[1])
