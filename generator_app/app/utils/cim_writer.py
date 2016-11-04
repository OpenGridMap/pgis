import io
import re
import shutil
import uuid
from collections import OrderedDict
from io import BytesIO
from os import makedirs
from os.path import exists, dirname, join, basename
from string import maketrans
from xml.dom.minidom import parse
from zipfile import ZipFile

import ogr
import osr
from CIM14.ENTSOE.Equipment.Core import BaseVoltage, GeographicalRegion, SubGeographicalRegion, ConnectivityNode, \
    Terminal
from CIM14.ENTSOE.Equipment.LoadModel import LoadResponseCharacteristic
from CIM14.ENTSOE.Equipment.Wires import PowerTransformer, SynchronousMachine, TransformerWinding
from CIM14.IEC61968.Common import Location, PositionPoint
from CIM14.IEC61970.Core import Substation
from CIM14.IEC61970.Generation.Production import GeneratingUnit
from CIM14.IEC61970.Wires import ACLineSegment
from CIM14.IEC61970.Wires import EnergyConsumer
from PyCIM import cimwrite
from geoalchemy2.shape import to_shape
from shapely.ops import linemerge

from load_estimator import LoadEstimator


class CimWriter:
    circuits = None
    centroid = None
    population_by_station_dict = None
    id = 0
    winding_types = ['primary', 'secondary', 'tertiary']
    base_voltages_dict = dict()

    region = SubGeographicalRegion(Region=GeographicalRegion(name='EU'))

    # osm id -> cim uuid
    uuid_by_osmid_dict = dict()
    # cim uuid -> cim object
    cimobject_by_uuid_dict = OrderedDict()
    # cim uuid -> cim connectivity node object
    connectivity_by_uuid_dict = dict()

    def __init__(self, circuits, centroid, ):
        self.circuits = circuits
        self.centroid = centroid
        self.base_voltages_dict = dict()
        self.uuid_by_osmid_dict = dict()
        self.cimobject_by_uuid_dict = OrderedDict()
        self.connectivity_by_uuid_dict = dict()

    def publish(self):
        self.region.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[self.region.UUID] = self.region

        self.add_location(self.centroid.x, self.centroid.y, is_center=True)

        total_line_length = 0
        for circuit in self.circuits:
            station1 = circuit.stations[0] if circuit.stations[0].id < circuit.stations[1].id else circuit.stations[1]
            station2 = circuit.stations[1] if circuit.stations[0].id < circuit.stations[1].id else circuit.stations[0]

            if 'station' == str(station1.type) or 'substation' == str(station1.type):
                connectivity_node1 = self.substation_to_cim(station1, circuit.voltage)
            elif 'plant' == str(station1.type) or 'generator' == str(station1.type):
                connectivity_node1 = self.generator_to_cim(station1, circuit.voltage)
            else:
                continue

            if 'station' == str(station2.type) or 'substation' == str(station2.type):
                connectivity_node2 = self.substation_to_cim(station2, circuit.voltage)
            elif 'plant' == str(station2.type) or 'generator' == str(station2.type):
                connectivity_node2 = self.generator_to_cim(station2, circuit.voltage)
            else:
                continue

            lines_wsg84 = []
            line_length = 0
            for line_wsg84 in circuit.powerlines:
                lines_wsg84.append(to_shape(line_wsg84.geom))
                line_length += line_wsg84.length
            line_wsg84 = linemerge(lines_wsg84)
            total_line_length += line_length
            self.line_to_cim(connectivity_node1, connectivity_node2, line_length, circuit.name, circuit.voltage,
                             line_wsg84.centroid.y, line_wsg84.centroid.x)

        self.attach_loads()

        base_dir = '../../models/{0}/'.format(self.uuid())
        dir_name = join(dirname(__file__), base_dir)

        if not exists(dir_name):
            makedirs(dir_name)

        file_name = dir_name + '/cim'

        cimwrite(self.cimobject_by_uuid_dict, file_name + '.xml', encoding='utf-8')
        cimwrite(self.cimobject_by_uuid_dict, file_name + '.rdf', encoding='utf-8')

        # pretty print cim file
        xml = parse(file_name + '.xml')

        pretty_xml_as_string = xml.toprettyxml(encoding='utf-8')
        matches = re.findall('#x[0-9a-f]{4}', pretty_xml_as_string)
        for match in matches:
            pretty_xml_as_string = pretty_xml_as_string.replace(match, unichr(int(match[2:len(match)], 16)))
        pretty_file = io.open(file_name + '_pretty.xml', 'w', encoding='utf8')
        pretty_file.write(unicode(pretty_xml_as_string))
        pretty_file.close()

        in_memory = BytesIO()
        zip_cim = ZipFile(in_memory, "a")
        zip_cim.write(file_name + '.xml', basename(file_name + '.xml'))
        zip_cim.write(file_name + '.rdf', basename(file_name + '.rdf'))
        zip_cim.write(file_name + '_pretty.xml', basename(file_name + '_pretty.xml'))
        zip_cim.close()
        shutil.rmtree(dir_name)
        in_memory.seek(0)
        return in_memory.read()

    def substation_to_cim(self, osm_substation, circuit_voltage):
        transformer_winding = None
        if osm_substation.id in self.uuid_by_osmid_dict:
            cim_substation = self.cimobject_by_uuid_dict[self.uuid_by_osmid_dict[osm_substation.id]]
            transformer = cim_substation.getEquipments()[0]  # TODO check if there is actually one equipment
            for winding in transformer.getTransformerWindings():
                if int(circuit_voltage) == winding.ratedU:
                    transformer_winding = winding
                    break
        else:
            cim_substation = Substation(name='SS_' + str(osm_substation.id), Region=self.region,
                                        Location=self.add_location(osm_substation.lat, osm_substation.lon))
            transformer = PowerTransformer(name='T_' + str(osm_substation.id) + '_' + CimWriter.escape_string(
                ';'.join(str(x) for x in osm_substation.voltage)) + '_' + CimWriter.escape_string(
                str(osm_substation.name.encode('utf-8') if osm_substation.name else None)),
                                           EquipmentContainer=cim_substation)
            cim_substation.UUID = str(CimWriter.uuid())
            transformer.UUID = str(CimWriter.uuid())
            self.cimobject_by_uuid_dict[cim_substation.UUID] = cim_substation
            self.cimobject_by_uuid_dict[transformer.UUID] = transformer
            self.uuid_by_osmid_dict[osm_substation.id] = cim_substation.UUID
        if not transformer_winding:
            transformer_winding = self.add_transformer_winding(osm_substation.id, int(circuit_voltage), transformer)
        return self.connectivity_by_uuid_dict[transformer_winding.UUID]

    def generator_to_cim(self, generator, circuit_voltage):
        if generator.id in self.uuid_by_osmid_dict:
            generating_unit = self.cimobject_by_uuid_dict[self.uuid_by_osmid_dict[generator.id]]
        else:
            generating_unit = GeneratingUnit(name='G_' + str(generator.id), maxOperatingP=generator.nominal_power,
                                             minOperatingP=0,
                                             nominalP=generator.nominal_power if generator.nominal_power else '',
                                             Location=self.add_location(generator.lat, generator.lon))
            synchronous_machine = SynchronousMachine(
                name='G_' + str(generator.id) + '_' + CimWriter.escape_string(str(generator.name.encode('utf-8') if generator.name else None)),
                operatingMode='generator', qPercent=0, x=0.01,
                r=0.01, ratedS='' if generator.nominal_power is None else generator.nominal_power, type='generator',
                GeneratingUnit=generating_unit, BaseVoltage=self.base_voltage(int(circuit_voltage)))
            generating_unit.UUID = str(CimWriter.uuid())
            synchronous_machine.UUID = str(CimWriter.uuid())
            self.cimobject_by_uuid_dict[generating_unit.UUID] = generating_unit
            self.cimobject_by_uuid_dict[synchronous_machine.UUID] = synchronous_machine
            self.uuid_by_osmid_dict[generator.id] = generating_unit.UUID
            connectivity_node = ConnectivityNode(name='CN_' + str(generator.id) + '_' + str(circuit_voltage))
            connectivity_node.UUID = str(CimWriter.uuid())
            self.cimobject_by_uuid_dict[connectivity_node.UUID] = connectivity_node
            terminal = Terminal(ConnectivityNode=connectivity_node, ConductingEquipment=synchronous_machine,
                                sequenceNumber=1)
            terminal.UUID = str(CimWriter.uuid())
            self.cimobject_by_uuid_dict[terminal.UUID] = terminal
            self.connectivity_by_uuid_dict[generating_unit.UUID] = connectivity_node
        return self.connectivity_by_uuid_dict[generating_unit.UUID]

    def line_to_cim(self, connectivity_node1, connectivity_node2, length, name, circuit_voltage, lat, lon):
        line = ACLineSegment(
            name=CimWriter.escape_string(str(name.encode('utf-8') if name else None)) + '_' + connectivity_node1.name + '_' + connectivity_node2.name, bch=0,
            r=0.3257, x=0.3153, r0=0.5336,
            x0=0.88025, length=length, BaseVoltage=self.base_voltage(int(circuit_voltage)),
            Location=self.add_location(lat, lon))
        line.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[line.UUID] = line
        terminal1 = Terminal(ConnectivityNode=connectivity_node1, ConductingEquipment=line, sequenceNumber=1)
        terminal1.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[terminal1.UUID] = terminal1
        terminal2 = Terminal(ConnectivityNode=connectivity_node2, ConductingEquipment=line, sequenceNumber=2)
        terminal2.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[terminal2.UUID] = terminal2

    @staticmethod
    def uuid():
        return uuid.uuid1()

    def increase_winding_type(self, winding):
        index = 0
        for winding_type in self.winding_types:
            if winding_type == winding.windingType:
                winding.windingType = self.winding_types[index + 1]
                break
            index += 1

    def add_transformer_winding(self, osm_substation_id, winding_voltage, transformer):
        new_transformer_winding = TransformerWinding(name='TW_' + str(osm_substation_id) + '_' + str(winding_voltage),
                                                     b=0, x=1.0, r=1.0, connectionType='Yn',
                                                     ratedU=winding_voltage, ratedS=5000000,
                                                     BaseVoltage=self.base_voltage(winding_voltage))
        # init with primary
        index = 0
        for winding in transformer.getTransformerWindings():
            # already a primary winding with at least as high voltage as the new one
            if winding.ratedU >= winding_voltage:
                index += 1
            else:
                self.increase_winding_type(winding)
        new_transformer_winding.windingType = self.winding_types[index]
        new_transformer_winding.setPowerTransformer(transformer)
        new_transformer_winding.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[new_transformer_winding.UUID] = new_transformer_winding
        connectivity_node = ConnectivityNode(name='CN_' + str(osm_substation_id) + '_' + str(winding_voltage))
        connectivity_node.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[connectivity_node.UUID] = connectivity_node
        terminal = Terminal(ConnectivityNode=connectivity_node, ConductingEquipment=new_transformer_winding,
                            sequenceNumber=1)
        terminal.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[terminal.UUID] = terminal
        self.connectivity_by_uuid_dict[new_transformer_winding.UUID] = connectivity_node
        return new_transformer_winding

    def attach_loads(self):
        for load in self.cimobject_by_uuid_dict.values():
            if isinstance(load, PowerTransformer):
                transformer = load
                osm_substation_id = transformer.name.split('_')[1]
                transformer_lower_voltage = CimWriter.determine_load_voltage(transformer)
                self.attach_load(osm_substation_id, transformer_lower_voltage, transformer)

    @staticmethod
    def determine_load_voltage(transformer):
        transformer_lower_voltage = transformer.getTransformerWindings()[0].ratedU
        for winding in transformer.getTransformerWindings():
            transformer_lower_voltage = winding.ratedU if winding.ratedU < transformer_lower_voltage \
                else transformer_lower_voltage
        return transformer_lower_voltage

    def attach_load(self, osm_substation_id, winding_voltage, transformer):
        transformer_winding = None
        if len(transformer.getTransformerWindings()) >= 2:
            for winding in transformer.getTransformerWindings():
                if winding_voltage == winding.ratedU:
                    transformer_winding = winding
                    break
        # add winding for lower voltage, if not already existing or
        # add winding if sub-station is a switching station (only one voltage level)
        if transformer_winding is None:
            transformer_winding = self.add_transformer_winding(osm_substation_id, winding_voltage, transformer)
        connectivity_node = self.connectivity_by_uuid_dict[transformer_winding.UUID]
        estimated_load = LoadEstimator.estimate_load(self.population_by_station_dict[str(
            osm_substation_id)]) if self.population_by_station_dict else 100000
        load_response_characteristic = LoadResponseCharacteristic(exponentModel=False, pConstantPower=estimated_load)
        load_response_characteristic.UUID = str(CimWriter.uuid())
        energy_consumer = EnergyConsumer(name='L_' + osm_substation_id, LoadResponse=load_response_characteristic,
                                         BaseVoltage=self.base_voltage(winding_voltage))
        energy_consumer.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[load_response_characteristic.UUID] = load_response_characteristic
        self.cimobject_by_uuid_dict[energy_consumer.UUID] = energy_consumer
        terminal = Terminal(ConnectivityNode=connectivity_node, ConductingEquipment=energy_consumer,
                            sequenceNumber=1)
        terminal.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[terminal.UUID] = terminal

    @staticmethod
    def escape_string(string):
        if string and string != u'None':
            string = unicode(string.translate(maketrans('-]^$/. ', '_______')), 'utf-8')
            hexstr = ''
            for c in string:
                if ord(c) > 127:
                    hexstr += "#x%04x" % ord(c)
                else:
                    hexstr += c
            return hexstr
        return ''

    def add_location(self, lat, lon, is_center=False):
        pp = PositionPoint(yPosition=lat, xPosition=lon)
        if is_center:
            pp.zPosition = 1
        pp.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[pp.UUID] = pp
        location = Location(PositionPoints=[pp])
        location.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[location.UUID] = location
        return location

    def base_voltage(self, voltage):
        if voltage in self.base_voltages_dict:
            return self.base_voltages_dict[voltage]
        base_voltage = BaseVoltage(nominalVoltage=voltage)
        base_voltage.UUID = str(CimWriter.uuid())
        self.cimobject_by_uuid_dict[base_voltage.UUID] = base_voltage
        self.base_voltages_dict[voltage] = base_voltage
        return base_voltage
