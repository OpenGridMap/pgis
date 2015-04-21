from imposm.parser import OSMParser
import psycopg2

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print "I am unable to connect to the database"


class PowerStationImporter(object):
    counter = 1

    def perform(self, nodes):
        for osmid, tags, coords in nodes:
            if 'power' in tags:
               query = 'INSERT INTO point("name", geom, properties) VALUES(\'{}\', ST_GeomFromText(\'{}\', 0), \'{}\')'.format("point #{}".format(self.counter), "POINT({} {})".format(coords[1], coords[0]), {}) 
               print query
               cur.execute(query) 
               self.counter += 1

importer = PowerStationImporter()
p = OSMParser(concurrency=4, nodes_callback=importer.perform)
p.parse('/home/headshota/Downloads/germany-latest.osm.pbf')
conn.commit()
