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

    coeffs_of_voltage = {
        220000: dict(wires_typical=2.0, r=0.08, x=0.32, c=11.5, i=1.3),
        380000: dict(wires_typical=4.0, r=0.025, x=0.25, c=13.7, i=2.6)
    }

    def __init__(self, circuits):
        self.circuits = circuits

    @staticmethod
    def convert_wire_names_to_numbers(string):
        wires_names = {'single': 1, 'double': 2, 'triple': 3, 'quad': 4}
        if string:
            wire_tokens = string.split('-')
            return [wires_names[x] if x in wires_names.keys() else 0 for x in wire_tokens]
        return []

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

    @staticmethod
    def convert_max_set_to_string(set_to_convert):
        if len(set_to_convert):
            return CSVWriter.sanitize_csv(str(sorted(set_to_convert)[-1]))
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
                if len(circuit['points']) == 2:
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
                    wires = set()
                    r_ohm_kms = None
                    x_ohm_kms = None
                    c_nf_kms = None
                    i_th_max_kms = None
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
                        if 'wires' in line_tags_keys:
                            wires.update(CSVWriter.convert_wire_names_to_numbers(
                                CSVWriter.sanitize_csv(line_part['properties']['tags']['wires'])))
                        if 'name' in line_tags_keys:
                            names.update([CSVWriter.sanitize_csv(line_part['properties']['tags']['name']) if
                                          line_part['properties']['tags']['name'] != 'None' else ''])
                        if 'type' in line_tags_keys:
                            types.update([line_part['properties']['tags']['type']])

                    if len(voltages) > 1 or len(cables) > 1 or len(frequencies) > 1 or len(types) > 1 or len(wires) > 1:
                        not_accurate = True

                    for station in [station1, station2]:
                        if station['id'] not in id_by_station_dict:
                            id_by_station_dict[station['id']] = station['id']
                            station_tags_keys = station['properties']['tags'].keys()
                            station_voltages = []
                            if 'voltage' in station_tags_keys:
                                station_voltages = [str(x) for x in station['properties']['tags']['voltage']]
                            not_accurate_node = False
                            # if len(station_voltages) > 1:
                            #     not_accurate_node = True

                            nodes_writer.writerow(
                                [str(station['id']),
                                 str(station['properties']['tags']['lon']),
                                 str(station['properties']['tags']['lat']),
                                 str(station['properties']['tags']['type']),
                                 ";".join(station_voltages),
                                 str(station['properties']['tags'][
                                         'frequency']) if 'frequency' in station_tags_keys else '',
                                 CSVWriter.sanitize_csv(
                                     station['properties']['tags']['name']) if 'name' in station_tags_keys
                                                                               and station['properties']['tags'][
                                                                                       'name'] != 'None' else '',
                                 CSVWriter.sanitize_csv(station['properties']['tags'][
                                                            'operator']) if 'operator' in station_tags_keys else '',
                                 'Yes' if not_accurate_node else ''])

                    length_selected = round(line_length)
                    cables_selected = CSVWriter.convert_max_set_to_string(cables)
                    voltage_selected = CSVWriter.convert_max_set_to_string(voltages)
                    wires_selected = CSVWriter.convert_max_set_to_string(wires)

                    voltage_selected_round = 0
                    if 360000 <= int(voltage_selected) <= 400000:
                        voltage_selected_round = 380000
                    elif 180000 <= int(voltage_selected) <= 260000:
                        voltage_selected_round = 220000

                    if length_selected and cables_selected and int(
                            voltage_selected_round) in self.coeffs_of_voltage and wires_selected:
                        coeffs = self.coeffs_of_voltage[int(voltage_selected_round)]
                        # Specific resistance of the transmission lines.
                        r_ohm_kms = coeffs['r'] / (int(wires_selected) / coeffs['wires_typical']) / (
                            int(cables_selected) / 3.0)
                        # Specific reactance of the transmission lines.
                        x_ohm_kms = coeffs['x'] / (int(wires_selected) / coeffs['wires_typical']) / (
                            int(cables_selected) / 3.0)
                        # Specific capacitance of the transmission lines.
                        c_nf_kms = coeffs['c'] * (int(wires_selected) / coeffs['wires_typical']) * (
                            int(cables_selected) / 3.0)
                        # Specific maximum current of the transmission lines.
                        i_th_max_kms = coeffs['i'] * (int(wires_selected) / coeffs['wires_typical']) * (
                            int(cables_selected) / 3.0)

                    lines_writer.writerow([str(line_counter),
                                           str(station1['id']),
                                           str(station2['id']),
                                           voltage_selected,
                                           cables_selected,
                                           CSVWriter.convert_max_set_to_string(types),
                                           CSVWriter.convert_max_set_to_string(frequencies),
                                           CSVWriter.convert_max_set_to_string(names),
                                           CSVWriter.convert_max_set_to_string(operators),
                                           str(length_selected),
                                           str(r_ohm_kms) if r_ohm_kms else '',
                                           str(x_ohm_kms) if x_ohm_kms else '',
                                           str(c_nf_kms) if c_nf_kms else '',
                                           str(i_th_max_kms) if i_th_max_kms else '',
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
