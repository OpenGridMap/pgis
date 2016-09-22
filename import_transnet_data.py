import psycopg2
import csv
import json

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")
    exit()


def transnet_powerline_importer(continent, country):
    cur.execute('''DELETE FROM transnet_powerline
                    WHERE country=%s;''', [
        country
    ])
    conn.commit()

    with open('./data/{0}/{1}/csv_lines_segment.csv'.format(continent, country), 'rb') as csvfile:
        powerlines = csv.reader(csvfile, delimiter=',')
        for row in powerlines:
            query = '''INSERT INTO transnet_powerline(geom, properties, country)
                                VALUES (ST_FlipCoordinates(%s), %s, %s)'''

            cur.execute(query, [
                row[7],
                json.dumps({"lon": row[1], "lat": row[2], "voltage": row[5], "type": row[6], "name": row[3],
                            "osm_id": row[4]}),
                country,
            ])
        conn.commit()


def transnet_station_importer(continent, country):
    cur.execute('''DELETE FROM transnet_station
                        WHERE country=%s;''', [
        country
    ])
    conn.commit()
    with open('./data/{0}/{1}/csv_nodes.csv'.format(continent, country), 'rb') as csvfile:
        powerlines = csv.reader(csvfile, delimiter=',')
        for row in powerlines:
            query = '''INSERT INTO transnet_station(geom, properties, country)
                                        VALUES (%s, %s, %s)'''

            cur.execute(query, [
                row[7],
                json.dumps({"lon": row[1], "lat": row[2], "voltage": row[5], "type": row[6], "name": row[3],
                            "osm_id": row[4]}),
                country,
            ])
        conn.commit()


transnet_powerline_importer('europe', 'austria')
transnet_station_importer('europe', 'austria')