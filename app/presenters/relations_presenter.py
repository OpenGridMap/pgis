from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import json
from app import db
from sqlalchemy.sql import text

# Presenter logic for Relations (plural).
class RelationsPresenter:
    def __init__(self, relations):
        self.relations = relations

    def as_osm_xml(self):
        osm_elem = Element('osm', {
            'version': '0.6',
            'generator': 'PGIS:http://github.com/OpenGridMap/pgis'
        })

        # ref_node_osmids: osm Ids of nodes that are part of a way
        # relation_member_node_osmids: osm Ids of nodes that are members of a relation
        #   We remove relation_member_node_osmids from ref_node_osmids later in
        #   the logic so that we don't repeat the same nodes in the XML.
        ref_node_osmids = []
        relation_member_node_osmids = []

        for relation_id, relation in self.relations.items():
            relation_elem = SubElement(osm_elem, 'relation', {
                'pgisId': str(relation['id']),
                'id': str(relation['properties']['osmid']),
                'version': "-1",
                'timestamp': ""
            })
            self.__buildXmlSubElementForTags(
                relation['properties']['tags'],
                relation_elem
            )

            for point in relation['points']:
                point_elem = SubElement(osm_elem, 'node', {
                    'lat': str(point['latlng'][0]),
                    'lon': str(point['latlng'][1]),
                    'id': str(point['properties']['osmid']),
                    'pgisId': str(point['id']),
                    'version': "-1",
                    'timestamp': ""
                })
                self.__buildXmlSubElementForTags(
                    point['properties']['tags'],
                    point_elem
                )
                relation_member_node_osmids.append(str(point['properties']['osmid']))

                member_elem = SubElement(relation_elem, 'member', {
                    'type': "node",
                    'ref': str(point['properties']['osmid']),
                    'role': ""
                })

            for powerline in relation['powerlines']:

                # our initial import scripts didn't import OSM IDs for powerlines
                if 'osmid' in powerline['properties']:
                    powerline_omsid = powerline['properties']['osmid']
                else:
                    powerline_omsid = "-1"

                powerline_elem = SubElement(osm_elem, 'way', {
                    'id': str(powerline_omsid),
                    'pgisId': str(powerline['id']),
                    'version': "-1",
                    'timestamp': ""
                })

                for point_id in powerline['properties']['refs']:
                    ref_elem = SubElement(powerline_elem, 'nd', {
                        'ref': str(point_id)
                    })
                    ref_node_osmids.append(str(point_id))

                self.__buildXmlSubElementForTags(
                    powerline['properties']['tags'],
                    powerline_elem
                )

                member_elem = SubElement(relation_elem, 'member', {
                    'type': "way",
                    'ref': str(powerline_omsid),
                    'role': ""
                })

        to_be_added_nodes = list(set(ref_node_osmids) - set(relation_member_node_osmids))
        ref_points = self.__points_with_osmids(to_be_added_nodes)

        for ref_point in ref_points:
            point_elem = SubElement(osm_elem, 'node', {
                'lat': str(ref_point['latlng'][0]),
                'lon': str(ref_point['latlng'][1]),
                'id': str(ref_point['properties']['osmid']),
                'pgisId': str(ref_point['id']),
                'version': "-1",
                'timestamp': ""

            })
            self.__buildXmlSubElementForTags(
                ref_point['properties']['tags'],
                point_elem
            )

        return tostring(osm_elem)


    def __buildXmlSubElementForTags(self, tags, parent_xml_element):
        if tags is not None:
            for tag, value in tags.items(): # tag.items() because tags is a dict
                tag_elem = SubElement(parent_xml_element, 'tag', {
                    'k': tag,
                    'v': value
                })

    def __points_with_osmids(self, osmids):
        query = text("""
            SELECT p.id AS p_id, ST_X(p.geom) AS p_x, ST_Y(p.geom) AS p_y,
                    p.properties AS p_prop
            FROM point p
            WHERE properties->>'osmid' IN :osm_ids
        """)
        point_rows = db.engine.execute(query, osm_ids = tuple(osmids))
        ref_points = []
        for row in point_rows:
            ref_points.append({
                'id': row['p_id'],
                'latlng': [row['p_x'], row['p_y']],
                'properties': row['p_prop']
            })

        return ref_points

