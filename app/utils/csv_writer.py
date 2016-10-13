import csv
import shutil
import uuid
from io import BytesIO
from os import makedirs

from os.path import dirname, exists, basename

from os.path import join
from zipfile import ZipFile


class CSVWriter:
    circuits = None

    def __init__(self, circuits):
        self.circuits = circuits

    def publish(self):

        id_by_station_dict = dict()
        station_counter = 1
        line_counter = 1

        base_dir = '../../models/{0}/'.format(uuid.uuid1())
        dir_name = join(dirname(__file__), base_dir)

        if not exists(dir_name):
            makedirs(dir_name)

        file_name = dir_name + '/csv'

        with open(file_name + '_nodes.csv', 'wt') as nodes_file, \
                open(file_name + '_lines.csv', 'wt') as lines_file:

            nodes_writer = csv.writer(nodes_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            nodes_writer.writerow(['id', 'lon', 'lat', 'name', 'osm_id', 'voltage', 'type'])

            lines_writer = csv.writer(lines_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            lines_writer.writerow(['id', 'n1_id', 'n2_id', 'length', 'voltage'])

            for key, circuit in self.circuits.items():
                station1 = circuit['points'][0] if circuit['points'][0]['id'] < circuit['points'][1]['id'] \
                    else circuit['points'][1]
                station2 = circuit['points'][1] if circuit['points'][0]['id'] < circuit['points'][1]['id'] \
                    else circuit['points'][0]
                line_length = 0
                for line_part in circuit['powerlines']:
                    line_length += line_part['properties']['tags']['length']
                for station in [station1, station2]:
                    if station['id'] not in id_by_station_dict:
                        id_by_station_dict[station['id']] = station_counter
                        nodes_writer.writerow(
                            [str(station_counter), str(station['properties']['tags']['lon']),
                             str(station['properties']['tags']['lat']),
                             str(station['properties']['tags']['name'].replace("'", '') if station['properties']['tags']['name'] else None),
                             str(station['id']),
                             str(station['properties']['tags']['voltage']), str(station['properties']['tags']['type'])])
                        station_counter += 1
                lines_writer.writerow(
                    [str(line_counter), str(id_by_station_dict[station1['id']]), str(id_by_station_dict[station2['id']]),
                     str(line_length), str(circuit['properties']['tags']['voltage'])])
                line_counter += 1

        in_memory = BytesIO()
        zip_cim = ZipFile(in_memory, "a")
        zip_cim.write(file_name + '_nodes.csv', basename(file_name + '_nodes.csv'))
        zip_cim.write(file_name + '_lines.csv', basename(file_name + '_lines.csv'))
        zip_cim.close()
        shutil.rmtree(dir_name)
        in_memory.seek(0)
        return in_memory.read()
