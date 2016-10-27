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

    # Aluminum R = 36/S(c.s.a)
    # Aluminum S = 2000mmsq
    # R = 36/2000 = 0.018 Ohms per km

    R = 0.018

    def __init__(self, circuits):
        self.circuits = circuits

    @staticmethod
    def try_parse_int(string):
        try:
            return int(string)
        except ValueError:
            return 0

    @staticmethod
    def sanitize_csv(string):
        if string:
            return string.replace("'", '').replace(';', '-')
        return ''

    @staticmethod
    def convert_set_to_string(set_to_convert):
        return CSVWriter.sanitize_csv('-'.join([str(v) for v in set_to_convert]))

    @staticmethod
    def convert_min_set_to_string(set_to_convert):
        if len(set_to_convert):
            return CSVWriter.sanitize_csv(str(sorted(set_to_convert)[0]))
        return ''

    def publish(self):

        id_by_station_dict = dict()
        line_counter = 1

        base_dir = '../../models/{0}/'.format(uuid.uuid1())
        dir_name = join(dirname(__file__), base_dir)

        if not exists(dir_name):
            makedirs(dir_name)

        file_name = dir_name + '/csv'

        with open(file_name + '_nodes.csv', 'wt') as nodes_file, \
                open(file_name + '_lines.csv', 'wt') as lines_file:

            nodes_writer = csv.writer(nodes_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            nodes_writer.writerow(
                ['n_id', 'longitude', 'latitude', 'type', 'voltage', 'frequency', 'name', 'operator', 'not_accurate'])

            lines_writer = csv.writer(lines_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            lines_writer.writerow(['l_id', 'n_id_start', 'n_id_end', 'voltage', 'cables', 'type',
                                   'frequency', 'name', 'operator', 'length_m', 'r_ohm_km', 'x_ohm_km', 'c_nf_km',
                                   'i_th_max_km', 'not_accurate'])

            for key, circuit in self.circuits.items():
                station1 = circuit['points'][0] if circuit['points'][0]['id'] < circuit['points'][1]['id'] \
                    else circuit['points'][1]
                station2 = circuit['points'][1] if circuit['points'][0]['id'] < circuit['points'][1]['id'] \
                    else circuit['points'][0]
                line_length = 0
                voltages = set()
                cables = set()
                frequencies = set()
                names = set()
                operators = set()
                r_ohm_kms = set()
                x_ohm_kms = set()
                c_nf_kms = set()
                i_th_max_kms = set()
                types = set()
                not_accurate = False

                for line_part in circuit['powerlines']:
                    line_length += line_part['properties']['tags']['length']
                    line_tags_keys = line_part['properties']['tags'].keys()
                    if 'voltage' in line_tags_keys:
                        voltages.update(line_part['properties']['tags']['voltage'])
                    if 'cables' in line_tags_keys:
                        cables.update([CSVWriter.try_parse_int(line_part['properties']['tags']['cables'])])
                    if 'frequency' in line_tags_keys:
                        frequencies.update([CSVWriter.try_parse_int(line_part['properties']['tags']['frequency'])])
                    if 'operator' in line_tags_keys:
                        operators.update([CSVWriter.sanitize_csv(
                            line_part['properties']['tags']['operator'] if line_part['properties']['tags'][
                                'operator'] else '')])
                    if 'name' in line_tags_keys:
                        names.update([CSVWriter.sanitize_csv(line_part['properties']['tags']['name']) if
                                      line_part['properties']['tags']['name'] != 'None' else ''])
                    if 'type' in line_tags_keys:
                        types.update([line_part['properties']['tags']['type']])

                if len(voltages) > 1 or len(cables) > 1 or len(frequencies) > 1 or len(types) > 1:
                    not_accurate = True

                for station in [station1, station2]:
                    if station['id'] not in id_by_station_dict:
                        id_by_station_dict[station['id']] = station['id']
                        station_tags_keys = station['properties']['tags'].keys()
                        station_voltages = []
                        if 'voltage' in station_tags_keys:
                            station_voltages = station['properties']['tags']['voltage']
                        not_accurate_node = False
                        if len(station_voltages) > 1:
                            not_accurate_node = True

                        nodes_writer.writerow(
                            [str(station['id']),
                             str(station['properties']['tags']['lon']),
                             str(station['properties']['tags']['lat']),
                             str(station['properties']['tags']['type']),
                             CSVWriter.convert_min_set_to_string(station_voltages),
                             str(station['properties']['tags'][
                                     'frequency']) if 'frequency' in station_tags_keys else '',
                             CSVWriter.sanitize_csv(
                                 station['properties']['tags']['name']) if 'name' in station_tags_keys
                                                                           and station['properties']['tags'][
                                                                                   'name'] != 'None' else '',
                             CSVWriter.sanitize_csv(station['properties']['tags'][
                                                        'operator']) if 'operator' in station_tags_keys else '',
                             'Yes' if not_accurate_node else ''])

                lines_writer.writerow([str(line_counter),
                                       str(station1['id']),
                                       str(station2['id']),
                                       CSVWriter.convert_min_set_to_string(voltages),
                                       CSVWriter.convert_min_set_to_string(cables),
                                       CSVWriter.convert_min_set_to_string(types),
                                       CSVWriter.convert_min_set_to_string(frequencies),
                                       CSVWriter.convert_set_to_string(names),
                                       CSVWriter.convert_set_to_string(operators),
                                       str(round(line_length)),
                                       CSVWriter.convert_min_set_to_string(r_ohm_kms),
                                       # http://www.electricalengineeringtoolbox.com/2009/11/calculation-of-cable-resistance.html
                                       CSVWriter.convert_min_set_to_string(x_ohm_kms),
                                       CSVWriter.convert_min_set_to_string(c_nf_kms),
                                       CSVWriter.convert_min_set_to_string(i_th_max_kms),
                                       'Yes' if not_accurate else ''])
                line_counter += 1

        in_memory = BytesIO()
        zip_cim = ZipFile(in_memory, "a")
        zip_cim.write(file_name + '_nodes.csv', basename(file_name + '_nodes.csv'))
        zip_cim.write(file_name + '_lines.csv', basename(file_name + '_lines.csv'))
        zip_cim.close()
        shutil.rmtree(dir_name)
        in_memory.seek(0)
        return in_memory.read()
