import io
import logging
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

from CIM14.ENTSOE.Equipment.Core import BaseVoltage, GeographicalRegion, SubGeographicalRegion, ConnectivityNode, \
    Terminal
from CIM14.ENTSOE.Equipment.Wires import PowerTransformer, SynchronousMachine, TransformerWinding
from CIM14.IEC61968.Common import Location, PositionPoint
from CIM14.IEC61970.Core import Substation
from CIM14.IEC61970.Generation.Production import GeneratingUnit
from CIM14.IEC61970.Wires import ACLineSegment
from PyCIM import cimwrite
from geoalchemy2.shape import to_shape
from shapely.ops import linemerge


class CimWriter:
    circuits = None
    centroid = None
    id = 0
    winding_types = ['primary', 'secondary', 'tertiary']
    root = logging.getLogger()
    base_voltages_dict = dict()

    region = SubGeographicalRegion(Region=GeographicalRegion(name='EU'))

    # osm id -> cim uuid
    uuid_by_osmid_dict = dict()
    # cim uuid -> cim object
    cimobject_by_uuid_dict = OrderedDict()
    # cim uuid -> cim connectivity node object
    connectivity_by_uuid_dict = dict()

    def __init__(self, circuits, centroid):
        self.circuits = circuits
        self.centroid = centroid
        self.base_voltages_dict = dict()
        self.uuid_by_osmid_dict = dict()
        self.cimobject_by_uuid_dict = OrderedDict()
        self.connectivity_by_uuid_dict = dict()
        self.root = logging.getLogger()

    def publish(self):
        self.region.UUID = str(self.uuid())
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
                self.root.error('Invalid circuit! - Skip circuit')
                continue

            if 'station' == str(station2.type) or 'substation' == str(station2.type):
                connectivity_node2 = self.substation_to_cim(station2, circuit.voltage)
            elif 'plant' == str(station2.type) or 'generator' == str(station2.type):
                connectivity_node2 = self.generator_to_cim(station2, circuit.voltage)
            else:
                self.root.error('Invalid circuit! - Skip circuit')
                continue

            lines_wsg84 = []
            line_length = 0
            for line_wsg84 in circuit.powerlines:
                lines_wsg84.append(to_shape(line_wsg84.geom))
                line_length += line_wsg84.length
            line_wsg84 = linemerge(lines_wsg84)
            total_line_length += line_length
            self.root.debug('Map line from (%lf,%lf) to (%lf,%lf) with length %s meters', station1.shape().centroid.y,
                            station1.shape().centroid.x, station2.shape().centroid.y, station2.shape().centroid.x,
                            str(line_length))
            self.line_to_cim(connectivity_node1, connectivity_node2, line_length, circuit.name, circuit.voltage,
                             line_wsg84.centroid.y, line_wsg84.centroid.x)

            # self.root.info('The inferred net\'s length is %s meters', str(total_line_length))

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
        if self.uuid_by_osmid_dict.has_key(osm_substation.osm_id):
            self.root.debug('Substation with OSMID %s already covered', str(osm_substation.osm_id))
            cim_substation = self.cimobject_by_uuid_dict[self.uuid_by_osmid_dict[osm_substation.osm_id]]
            transformer = cim_substation.getEquipments()[0]  # TODO check if there is actually one equipment
            for winding in transformer.getTransformerWindings():
                if int(circuit_voltage) == winding.ratedU:
                    self.root.debug('Transformer of Substation with OSMID %s already has winding for voltage %s',
                                    str(osm_substation.osm_id), circuit_voltage)
                    transformer_winding = winding
                    break
        else:
            self.root.debug('Create CIM Substation for OSMID %s', str(osm_substation.osm_id))
            cim_substation = Substation(name='SS_' + str(osm_substation.osm_id), Region=self.region,
                                        Location=self.add_location(osm_substation.lat, osm_substation.lon))
            transformer = PowerTransformer(name='T_' + str(osm_substation.osm_id) + '_' + CimWriter.escape_string(str(
                osm_substation.voltage)) + '_' + CimWriter.escape_string(
                str(osm_substation.name.encode('utf-8') if osm_substation.name else None)),
                                           EquipmentContainer=cim_substation)
            cim_substation.UUID = str(self.uuid())
            transformer.UUID = str(self.uuid())
            self.cimobject_by_uuid_dict[cim_substation.UUID] = cim_substation
            self.cimobject_by_uuid_dict[transformer.UUID] = transformer
            self.uuid_by_osmid_dict[osm_substation.osm_id] = cim_substation.UUID
        if transformer_winding is None:
            transformer_winding = self.add_transformer_winding(osm_substation.osm_id, int(circuit_voltage), transformer)
        return self.connectivity_by_uuid_dict[transformer_winding.UUID]

    def generator_to_cim(self, generator, circuit_voltage):
        if self.uuid_by_osmid_dict.has_key(generator.osm_id):
            self.root.debug('Generator with OSMID %s already covered', str(generator.osm_id))
            generating_unit = self.cimobject_by_uuid_dict[self.uuid_by_osmid_dict[generator.osm_id]]
        else:
            self.root.debug('Create CIM Generator for OSMID %s', str(generator.osm_id))
            generating_unit = GeneratingUnit(name='G_' + str(generator.osm_id), maxOperatingP=generator.nominal_power,
                                             minOperatingP=0,
                                             nominalP='' if generator.nominal_power is None else generator.nominal_power,
                                             Location=self.add_location(generator.lat, generator.lon))
            synchronous_machine = SynchronousMachine(
                name='G_' + str(generator.osm_id) + '_' + CimWriter.escape_string(str(generator.name.encode('utf-8') if generator.name else None)),
                operatingMode='generator', qPercent=0, x=0.01,
                r=0.01, ratedS='' if generator.nominal_power is None else generator.nominal_power, type='generator',
                GeneratingUnit=generating_unit, BaseVoltage=self.base_voltage(int(circuit_voltage)))
            generating_unit.UUID = str(self.uuid())
            synchronous_machine.UUID = str(self.uuid())
            self.cimobject_by_uuid_dict[generating_unit.UUID] = generating_unit
            self.cimobject_by_uuid_dict[synchronous_machine.UUID] = synchronous_machine
            self.uuid_by_osmid_dict[generator.osm_id] = generating_unit.UUID
            connectivity_node = ConnectivityNode(name='CN_' + str(generator.osm_id) + '_' + str(circuit_voltage))
            connectivity_node.UUID = str(self.uuid())
            self.cimobject_by_uuid_dict[connectivity_node.UUID] = connectivity_node
            terminal = Terminal(ConnectivityNode=connectivity_node, ConductingEquipment=synchronous_machine,
                                sequenceNumber=1)
            terminal.UUID = str(self.uuid())
            self.cimobject_by_uuid_dict[terminal.UUID] = terminal
            self.connectivity_by_uuid_dict[generating_unit.UUID] = connectivity_node
        return self.connectivity_by_uuid_dict[generating_unit.UUID]

    def line_to_cim(self, connectivity_node1, connectivity_node2, length, name, circuit_voltage, lat, lon):
        line = ACLineSegment(
            name=CimWriter.escape_string(str(name.encode('utf-8') if name else None)) + '_' + connectivity_node1.name.encode(
                'utf-8') if connectivity_node1.name else None + '_' +
                                                         connectivity_node2.name.encode(
                                                             'utf-8') if connectivity_node2.name else None,
            bch=0,
            r=0.3257, x=0.3153, r0=0.5336,
            x0=0.88025, length=length, BaseVoltage=self.base_voltage(int(circuit_voltage)),
            Location=self.add_location(lat, lon))
        line.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[line.UUID] = line
        terminal1 = Terminal(ConnectivityNode=connectivity_node1, ConductingEquipment=line, sequenceNumber=1)
        terminal1.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[terminal1.UUID] = terminal1
        terminal2 = Terminal(ConnectivityNode=connectivity_node2, ConductingEquipment=line, sequenceNumber=2)
        terminal2.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[terminal2.UUID] = terminal2

    def uuid(self):
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
        new_transformer_winding.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[new_transformer_winding.UUID] = new_transformer_winding
        connectivity_node = ConnectivityNode(name='CN_' + str(osm_substation_id) + '_' + str(winding_voltage))
        connectivity_node.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[connectivity_node.UUID] = connectivity_node
        terminal = Terminal(ConnectivityNode=connectivity_node, ConductingEquipment=new_transformer_winding,
                            sequenceNumber=1)
        terminal.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[terminal.UUID] = terminal
        self.connectivity_by_uuid_dict[new_transformer_winding.UUID] = connectivity_node
        return new_transformer_winding

    @staticmethod
    def escape_string(string):
        if string and string != u'None':
            str = unicode(string.translate(maketrans('-]^$/. ', '_______')), 'utf-8')
            hexstr = ''
            for c in str:
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
        pp.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[pp.UUID] = pp
        location = Location(PositionPoints=[pp])
        location.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[location.UUID] = location
        return location

    def base_voltage(self, voltage):
        if self.base_voltages_dict.has_key(voltage):
            return self.base_voltages_dict[voltage];
        base_voltage = BaseVoltage(nominalVoltage=voltage)
        base_voltage.UUID = str(self.uuid())
        self.cimobject_by_uuid_dict[base_voltage.UUID] = base_voltage
        self.base_voltages_dict[voltage] = base_voltage
        return base_voltage
