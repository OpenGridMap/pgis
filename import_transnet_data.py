import csv
import json
import urllib
from os import makedirs
from os.path import exists
from os.path import dirname
from os.path import join
from os import walk

import psycopg2

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")
    exit()

base_dir = './data'


def download_latest_relation_files():
    try:
        base_url = 'https://raw.githubusercontent.com/OpenGridMap/transnet/planet-models'

        # Download planet json to get the list of continent
        planet_folder = '{0}/planet_json/'.format(base_dir)
        if not exists(planet_folder):
            makedirs(planet_folder)

        print('Downloading planet config json')
        urllib.URLopener().retrieve('{0}/app/meta/planet.json'.format(base_url),
                                    '{0}/planet_json/planet.json'.format(base_dir))

        # For each continent in the planet json, we should now download the continent json
        # and then for each country in the continent download the relations file.

        with open('{0}/planet_json/planet.json'.format(base_dir), 'r+') as planet_file:
            continents = json.load(planet_file)
            for continent in continents:
                print('Downloading {0} config json'.format(continent))
                urllib.URLopener().retrieve('{0}/app/meta/{1}.json'.format(base_url, continent),
                                            '{0}/planet_json/{1}.json'.format(base_dir, continent))
                with open('{0}/planet_json/{1}.json'.format(base_dir, continent), 'r+') as continent_file:
                    countries = json.load(continent_file)
                    for country in countries:
                        country_folder = '{0}/relations/{1}/{2}/'.format(base_dir, continent, country)
                        if not exists(country_folder):
                            makedirs(country_folder)

                        print('Downloading {0} relation json'.format(country))
                        try:
                            urllib.URLopener().retrieve(
                                '{0}/models/{1}/{2}/relations.json'.format(base_url, continent, country),
                                '{0}/relations/{1}/{2}/relations.json'.format(base_dir, continent, country))
                        except IOError as e:
                            print('relation for {0} not found.'.format(country))
    except Exception as e:
        print(e)
        exit()


def find_and_import_relation_files():
    try:
        dirs = [x[0] for x in walk(join(dirname(__file__), '{0}/relations/'.format(base_dir)))]
        for dir in dirs[1:]:
            relation_path = '{0}/relations.json'.format(dir)
            if exists(relation_path):
                transnet_import_relations(relation_path)
            else:
                print('relations  not exist {0}'.format(dir))

    except Exception as e:
        print(e)
        exit()


def try_parse_int(string):
    try:
        return int(string)
    except ValueError as e:
        print(e)
        raise ValueError()


def transnet_import_relations(json_file):
    country = json_file.split('/')[-2]
    cur.execute('''DELETE FROM transnet_powerline
                    WHERE country=%s;''', [
        country
    ])
    cur.execute('''DELETE FROM transnet_station
                        WHERE country=%s;''', [
        country
    ])
    cur.execute('''DELETE FROM transnet_relation
                        WHERE country=%s;''', [
        country
    ])
    conn.commit()

    query_relation = '''INSERT INTO transnet_relation(country, ref, name, voltage)
                                    VALUES (%s, %s, %s, %s) RETURNING id'''

    query_powerline = '''INSERT INTO transnet_powerline(country, geom, tags, raw_geom, voltage, type, nodes,
                                                                  lat, lon, cables, name, length, osm_id, relation_id)
                                                    VALUES (%s, ST_FlipCoordinates(%s), %s, %s,%s, %s, %s, %s,%s, %s, %s, %s
                                                    ,%s, %s)'''
    query_station = '''INSERT INTO transnet_station(country, geom, tags, raw_geom, lat, lon, name,
                                                      length, osm_id, nodes, voltage, type, relation_id)
                                                    VALUES (%s, ST_FlipCoordinates(%s), %s, %s,%s, %s, %s, %s,%s, %s, %s, %s
                                                    ,%s)'''

    powerline_tags = ['line', 'cable', 'minor_line']
    station_tags = ['substation', 'station', 'sub_station', 'plant', 'generator']

    with open(json_file, 'r+') as relations_file:
        relations = json.load(relations_file)
        for relation in relations:
            cur.execute(query_relation, [country, relation['ref'], relation['name'], relation['voltage']])
            relation_id = cur.fetchone()[0]
            for member in relation['members']:
                if member['type'] in powerline_tags:
                    cur.execute(query_powerline, [country,
                                                  member['geom'],
                                                  json.dumps(
                                                      {}),
                                                  member['raw_geom'],
                                                  member['voltage'],
                                                  member['type'],
                                                  member['nodes'],
                                                  member['lat'],
                                                  member['lon'],
                                                  member['cables'],
                                                  member['name'],
                                                  member['length'],
                                                  member['id'],
                                                  relation_id
                                                  ])
                elif member['type'] in station_tags:
                    cur.execute(query_station, [country,
                                                member['geom'],
                                                json.dumps(
                                                    {}),
                                                member['raw_geom'],
                                                member['lat'],
                                                member['lon'],
                                                member['name'],
                                                member['length'],
                                                member['id'],
                                                member['nodes'],
                                                member['voltage'],
                                                member['type'],
                                                relation_id
                                                ])

        conn.commit()


# download_latest_relation_files()
# find_and_import_relation_files()
transnet_import_relations('/home/epezhman/Projects/pgis/./data/relations/europe/austria/relations.json')





# query = '''INSERT INTO transnet_relation(geom, properties, country)
#                                 VALUES (ST_FlipCoordinates(%s), %s, %s)'''
#
#             cur.execute(query, [
#                 row[7],
#                 json.dumps({"lon": row[1], "lat": row[2], "voltage": row[5], "type": row[6], "name": row[3],
#                             "osm_id": row[4]}),
#                 country,
#             ])
