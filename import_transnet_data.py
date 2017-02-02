import ast
import json
import urllib
from datetime import date
from os import makedirs
from os import walk
from os.path import dirname
from os.path import exists
from os.path import join
from subprocess import call

import psycopg2

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")
    exit()

base_dir = './data'


def download_large_relations(base_url, continent, country):
    file_extensions = ['aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak']
    for file_extension in file_extensions:
        try:
            urllib.URLopener().retrieve(
                '{0}/models/{1}/{2}/_relations{3}'.format(base_url, continent, country, file_extension),
                '{0}/relations/{1}/{2}/_relations{3}'.format(base_dir, continent, country, file_extension))
        except IOError as e:
            print('relations part {0} for {1} not found.'.format(file_extension, country))
    try:
        command = 'cat {0}/relations/{1}/{2}/_relations* > {0}/relations/{1}/{2}/relations.json ' \
                  '&& rm {0}/relations/{1}/{2}/_relations*'.format(base_dir, continent, country, )
        call(command, shell=True)
    except Exception as e:
        print(e)


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

        query_country = '''INSERT INTO transnet_country(continent, country, voltages)
                                            VALUES (%s, %s, %s);'''

        cur.execute('''DELETE FROM transnet_country;''')
        conn.commit()
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
                        voltages = [try_parse_int(x) for x in countries[country]['voltages'].split('|')]
                        cur.execute(query_country, [continent, country, voltages])
                        conn.commit()
                        country_folder = '{0}/relations/{1}/{2}/'.format(base_dir, continent, country)
                        if not exists(country_folder):
                            makedirs(country_folder)

                        print('Downloading {0} relation json'.format(country))
                        try:
                            pass
                            urllib.URLopener().retrieve(
                                '{0}/models/{1}/{2}/relations.json'.format(base_url, continent, country),
                                '{0}/relations/{1}/{2}/relations.json'.format(base_dir, continent, country))
                        except IOError as e:
                            print('relation for {0} not found.'.format(country))
                            download_large_relations(base_url, continent, country)
    except Exception as e:
        print(e)


def find_and_import_relation_files():
    try:
        cur.execute('''DELETE FROM transnet_relation_powerline;''')
        cur.execute('''DELETE FROM transnet_relation_station ''')
        cur.execute('''DELETE FROM transnet_powerline ''')
        cur.execute('''DELETE FROM transnet_station ''')
        cur.execute('''DELETE FROM transnet_relation ''')

        conn.commit()

        dirs = [x[0] for x in walk(join(dirname(__file__), '{0}/relations/'.format(base_dir)))]
        for dir in dirs[1:]:
            relation_path = '{0}/relations.json'.format(dir)
            if exists(relation_path):
                transnet_import_relations(relation_path)
            else:
                print('relations not exist {0}'.format(dir))

    except Exception as e:
        print(e)


def try_parse_int(string):
    try:
        return int(string)
    except ValueError as e:
        return 0


def transnet_add_last_update():
    cur.execute('''INSERT INTO transnet_stats(last_updated) VALUES (%s)''', [date.today()])

    conn.commit()


def transnet_delete_country(country):
    cur.execute('''DELETE FROM transnet_relation_powerline WHERE country=%s;''', [country])
    cur.execute('''DELETE FROM transnet_relation_station WHERE country=%s;''', [country])
    cur.execute('''DELETE FROM transnet_powerline WHERE country=%s;''', [country])
    cur.execute('''DELETE FROM transnet_station WHERE country=%s;''', [country])
    cur.execute('''DELETE FROM transnet_relation WHERE country=%s;''', [country])

    conn.commit()


def transnet_import_relations(json_file):
    try:
        country = json_file.split('/')[-2]
        print('importing relations of {0}'.format(country))

        query_relation = '''INSERT INTO transnet_relation(country, ref, name, voltage)
                                        VALUES (%s, %s, %s, %s) RETURNING id'''

        query_powerline = '''INSERT INTO transnet_powerline(country, geom, tags, raw_geom, voltage, type, nodes,
                                                                      lat, lon, cables, name, length, osm_id, srs_geom, osm_replication)
                                                        VALUES (%s, ST_FlipCoordinates(%s), %s  , %s,%s, %s, %s, %s,%s, %s, %s, %s
                                                        ,%s ,ST_FlipCoordinates(%s), %s) RETURNING id'''

        query_station = '''INSERT INTO transnet_station(country, geom, tags, raw_geom, lat, lon, name,
                                                          length, osm_id, voltage, type, osm_replication)
                                                        VALUES (%s, ST_FlipCoordinates(%s), %s, %s,%s, %s, %s, %s,%s, %s
                                                          , %s, %s) RETURNING id'''

        query_relation_station = '''INSERT INTO transnet_relation_station(country, relation_id, station_id)
                                                VALUES (%s, %s, %s)'''

        query_relation_powerline = '''INSERT INTO transnet_relation_powerline(country, relation_id, powerline_id)
                                                VALUES (%s, %s, %s)'''

        query_powerline_count = '''SELECT count(id) FROM transnet_powerline WHERE osm_id = %s'''
        query_station_count = '''SELECT count(id) FROM transnet_station WHERE osm_id = %s'''

        query_powerline_get_one_id = '''SELECT id FROM transnet_powerline WHERE osm_id = %s LIMIT 1'''
        query_station_get_one_id = '''SELECT id FROM transnet_station WHERE osm_id = %s LIMIT 1'''

        query_powerline_increment_osm_rep = '''UPDATE transnet_powerline SET osm_replication = osm_replication + 1 WHERE id = %s'''
        query_station_increment_osm_rep = '''UPDATE transnet_station SET osm_replication = osm_replication + 1 WHERE id = %s'''

        powerline_tags = ['line', 'cable', 'minor_line']
        station_tags = ['substation', 'station', 'sub_station', 'plant', 'generator']

        with open(json_file, 'r+') as relations_file:
            relations = json.load(relations_file)
            for relation in relations:
                cur.execute(query_relation, [country, relation['ref'], relation['name'], relation['voltage']])
                relation_id = cur.fetchone()[0]
                for member in relation['members']:
                    voltages = [try_parse_int(x) for x in member['voltage'].split(';')]
                    if member['type'] in powerline_tags:

                        cur.execute(query_powerline_count, [member['id']])
                        powerline_count = cur.fetchone()[0]
                        if powerline_count:
                            cur.execute(query_powerline_get_one_id, [member['id']])
                            powerline_id = cur.fetchone()[0]
                            cur.execute(query_powerline_increment_osm_rep, [powerline_id])
                        else:
                            tags_list = ast.literal_eval(member['tags'])
                            tags = json.dumps(dict(zip(tags_list[::2], tags_list[1::2])))
                            cur.execute(query_powerline, [country,
                                                          member['geom'],
                                                          tags,
                                                          member['raw_geom'],
                                                          voltages,
                                                          member['type'],
                                                          member['nodes'],
                                                          member['lat'],
                                                          member['lon'],
                                                          try_parse_int(member['cables']),
                                                          member['name'],
                                                          member['length'],
                                                          member['id'],
                                                          member['srs_geom'],
                                                          1])
                            powerline_id = cur.fetchone()[0]

                        cur.execute(query_relation_powerline, [country, relation_id, powerline_id])

                    elif member['type'] in station_tags:
                        cur.execute(query_station_count, [member['id']])
                        station_count = cur.fetchone()[0]
                        if station_count:
                            cur.execute(query_station_get_one_id, [member['id']])
                            station_id = cur.fetchone()[0]
                            cur.execute(query_station_increment_osm_rep, [station_id])
                        else:
                            tags_list = [x.replace('"', "").replace('\\', "") for x in
                                         member['tags'].replace(',', '=>').split('=>')]
                            tags = json.dumps(dict(zip(tags_list[::2], tags_list[1::2])))
                            cur.execute(query_station, [country,
                                                        member['geom'],
                                                        tags,
                                                        member['raw_geom'],
                                                        member['lat'],
                                                        member['lon'],
                                                        member['name'],
                                                        member['length'],
                                                        member['id'],
                                                        voltages,
                                                        member['type'],
                                                        1])
                            station_id = cur.fetchone()[0]
                        cur.execute(query_relation_station, [country, relation_id, station_id])
                    conn.commit()
    except Exception as e:
        print(e)


def transnet_import_lines_with_missing_data(json_file):
    try:
        country = json_file.split('/')[-2]
        print('importing lines with missing data of {0}'.format(country))

        cur.execute('''DELETE FROM transnet_line_missing_data WHERE country=%s;''', [country])

        query_powerline = '''INSERT INTO transnet_line_missing_data(country, geom, tags, raw_geom, voltage, type, nodes,
                                                                      lat, lon, cables, name, length, osm_id, srs_geom, estimated_voltage, estimated_cables)
                                                        VALUES (%s, ST_FlipCoordinates(%s), %s  , %s,%s, %s, %s, %s,%s, %s, %s, %s
                                                        ,%s ,ST_FlipCoordinates(%s), %s, %s)'''
        query_powerline_count = '''SELECT count(id) FROM transnet_line_missing_data WHERE osm_id = %s'''

        with open(json_file, 'r+') as lines_file:
            lines = json.load(lines_file)
            for line in lines:
                voltages = [try_parse_int(x) for x in line['voltage'].split(';')]
                estimated_voltages = [try_parse_int(x) for x in line['estimated_voltage'].split(';')]
                estimated_cables = [try_parse_int(x) for x in line['estimated_cables'].split(';')]
                cur.execute(query_powerline_count, [line['id']])
                powerline_count = cur.fetchone()[0]
                if not powerline_count:
                    tags_list = ast.literal_eval(line['tags'])
                    tags = json.dumps(dict(zip(tags_list[::2], tags_list[1::2])))
                    cur.execute(query_powerline, [country,
                                                  line['geom'],
                                                  tags,
                                                  line['raw_geom'],
                                                  voltages,
                                                  line['type'],
                                                  line['nodes'],
                                                  line['lat'],
                                                  line['lon'],
                                                  try_parse_int(line['cables']),
                                                  line['name'],
                                                  line['length'],
                                                  line['id'],
                                                  line['srs_geom'],
                                                  estimated_voltages,
                                                  estimated_cables])

                conn.commit()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    # download_latest_relation_files()
    # find_and_import_relation_files()
    # transnet_add_last_update()

    # transnet_delete_country('germany')
    # transnet_import_relations('/home/epezhman/Projects/pgis/./data/relations/planet/germany/relations.json')
    # transnet_delete_country('usa')
    # transnet_import_relations('/home/epezhman/Projects/pgis/./data/relations/planet/usa/relations.json')
    # transnet_delete_country('india')
    # transnet_import_relations('/home/epezhman/Projects/pgis/./data/relations/asia/india/relations.json')

    transnet_import_lines_with_missing_data('/home/epezhman/Projects/pgis/./data/relations/europe/austria/lines_with_missing_data.json')
