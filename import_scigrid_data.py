import csv

import psycopg2

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")
    exit()

base_dir = './scigird'


def try_parse_int(string):
    try:
        return int(string)
    except ValueError as e:
        return 0


def try_parse_float(string):
    try:
        return float(string)
    except ValueError as e:
        return 0


def import_files():
    try:
        cur.execute('''DELETE FROM scigrid_station;''')
        cur.execute('''DELETE FROM scigrid_powerline;''')

        file_names = ['gridkit_europe-highvoltage-links', 'gridkit_europe-highvoltage-vertices']

        conn.commit()
        query_powerline = '''INSERT INTO
                             scigrid_powerline(l_id, v_id_1, v_id_2, voltage, cables, wires, frequency,
                             name, operator, ref, length_m, r_ohmkm, x_ohmkm, c_nfkm, i_th_max_a, from_relation, geom)
                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,ST_FlipCoordinates(%s))'''

        query_station = '''INSERT INTO
                           scigrid_station(v_id, lon, lat, type, voltage, frequency, name, operator, ref, geom)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,ST_FlipCoordinates(%s))'''
        print('Importing lines')
        with open('{0}/{1}.csv'.format(base_dir, file_names[0])) as lines_file:
            reader = csv.reader(lines_file, delimiter=',', quotechar='"')
            next(reader, None)
            for row in reader:
                voltages = [try_parse_int(x) for x in row[0].split(';')]
                cables = [try_parse_int(x) for x in row[4].split(';')]
                wires = [try_parse_int(x) for x in row[5].split(';')]
                frequency = [try_parse_int(x) for x in row[6].split(';')]
                cur.execute(query_powerline, [int(row[0]),
                                              int(row[1]),
                                              int(row[2]),
                                              voltages,
                                              cables,
                                              wires,
                                              frequency,
                                              str(row[7]),
                                              str(row[8]),
                                              str(row[9]),
                                              try_parse_float(str(row[10])),
                                              try_parse_float(str(row[11])),
                                              try_parse_float(str(row[12])),
                                              try_parse_float(str(row[13])),
                                              try_parse_float(str(row[14])),
                                              True if row[15] else False,
                                              row[16],
                                              ])
        conn.commit()

        print('Importing stations')
        with open('{0}/{1}.csv'.format(base_dir, file_names[1])) as lines_file:
            reader = csv.reader(lines_file, delimiter=',', quotechar='"')
            next(reader, None)
            for row in reader:
                voltages = [try_parse_int(x) for x in row[4].split(';')]
                frequency = [try_parse_int(x) for x in row[5].split(';')]
                cur.execute(query_station, [int(row[0]),
                                            try_parse_float(str(row[1])),
                                            try_parse_float(str(row[2])),
                                            str(row[3]),
                                            voltages,
                                            frequency,
                                            str(row[6]),
                                            str(row[7]),
                                            str(row[8]),
                                            row[9],
                                            ])

        conn.commit()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    import_files()
