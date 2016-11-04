from xml.etree.ElementTree import Element, SubElement, tostring

from sqlalchemy.sql import text

from app import db


# Presenter logic for Relations (plural).
class RelationsPresenter:
    def __init__(self, relations, transnet=False):
        self.relations = relations
        self.transnet = transnet

    def as_osm_xml(self):
        osm_elem = Element('osm', {
            'version': '0.6',
            'generator': 'PGIS:http://github.com/OpenGridMap/pgis'
        })

        relation_member_node_osmids = []

        powerline_ids = []
        powerline_xml_elems = {}

        for relation_id, relation in self.relations.items():
            relation_elem = SubElement(osm_elem, 'relation', {
                'pgisId': str(relation['id']),
                'id': str(relation['properties']['osmid']),
                'version': "-1",
                'timestamp': ""
            })
            self.__buildXmlSubElementForTags(
                {key: str(relation['properties']['tags'][key]) for key in relation['properties']['tags'].keys()},
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
                    {key: str(point['properties']['tags'][key]) for key in point['properties']['tags'].keys()},
                    point_elem
                )
                relation_member_node_osmids.append(str(point['properties']['osmid']))

                member_elem = SubElement(relation_elem, 'member', {
                    'type': "node",
                    'ref': str(point['properties']['osmid']),
                    'role': ""
                })

            relation_powerline_index = 0
            for powerline in relation['powerlines']:

                # our initial import scripts didn't import OSM IDs for powerlines
                if 'osmid' in powerline['properties']:
                    powerline_omsid = powerline['properties']['osmid']
                else:
                    # Generate powerline's id based on relation id if we don;t have it
                    # We assume appending "-000" will prevent any clashes with
                    # the actual OSMIDs later in future
                    powerline_omsid = "-000" + str(relation['id']) + str(relation_powerline_index)

                relation_powerline_index = relation_powerline_index + 1

                powerline_elem = SubElement(osm_elem, 'way', {
                    'id': str(powerline_omsid),
                    'pgisId': str(powerline['id']),
                    'version': "-1",
                    'timestamp': ""
                })

                powerline_ids.append(int(powerline['id']))
                powerline_xml_elems[int(powerline['id'])] = powerline_elem

                self.__buildXmlSubElementForTags(
                    {key: str(powerline['properties']['tags'][key]) for key in powerline['properties']['tags'].keys()},
                    powerline_elem
                )

                member_elem = SubElement(relation_elem, 'member', {
                    'type': "way",
                    'ref': str(powerline_omsid),
                    'role': ""
                })

        # The logic following will fetch the points from a powerline's LINESTRING
        # and generate the XML for those points and adds +nd+ sub element to the
        # powerline element.
        if self.transnet:
            ref_points = self.__points_for_powerlines_transnet(powerline_ids)
        else:
            ref_points = self.__points_for_powerlines(powerline_ids)
        index = 0
        for ref_point in ref_points:
            point_powerline_id = ref_point['powerline_id']
            # Generate point id based on powerline id and index
            # We assume appending "-00" will prevent any clashes with
            # the actual OSMIDs later in future
            point_powerline_link_id = "-00" + str(ref_point['powerline_id']) + str(index)
            point_elem = SubElement(osm_elem, 'node', {
                'lat': str(ref_point['latlng'][0]),
                'lon': str(ref_point['latlng'][1]),
                'id': point_powerline_link_id,
                'version': "-1",
                'timestamp': ""

            })
            index = index + 1;
            ref_elem = SubElement(powerline_xml_elems[point_powerline_id], 'nd', {
                'ref': str(point_powerline_link_id)
            })

        return tostring(osm_elem)

    def __buildXmlSubElementForTags(self, tags, parent_xml_element):
        if tags is not None:
            for tag, value in tags.items():  # tag.items() because tags is a dict
                tag_elem = SubElement(parent_xml_element, 'tag', {
                    'k': tag,
                    'v': value
                })
        for tag, value in tags.items():  # tag.items() because tags is a dict
            tag_elem = SubElement(parent_xml_element, 'tag', {
                'key': tag,
                'value': str(value)
            })

    def __points_for_powerlines(self, powerline_ids):
        query = text("""
            SELECT ST_X(geom) AS p_x, ST_Y(geom) AS p_y, id
            FROM (
              SELECT (ST_DumpPoints(g.geom)).*, g.id
              FROM(
                SELECT geom, id FROM powerline WHERE id IN :powerline_ids
              ) AS g
            ) j;
         """)
        point_rows = db.engine.execute(query, powerline_ids=tuple(powerline_ids))
        ref_points = []
        for row in point_rows:
            ref_points.append({
                'latlng': [row['p_x'], row['p_y']],
                'powerline_id': row['id']
            })

        return ref_points

    def __points_with_osmids(self, osmids):
        query = text("""
            SELECT p.id AS p_id, ST_X(p.geom) AS p_x, ST_Y(p.geom) AS p_y,
                    p.properties AS p_prop
            FROM point p
            WHERE properties->>'osmid' IN :osm_ids
        """)
        point_rows = db.engine.execute(query, osm_ids=tuple(osmids))
        ref_points = []
        for row in point_rows:
            ref_points.append({
                'id': row['p_id'],
                'latlng': [row['p_x'], row['p_y']],
                'properties': row['p_prop']
            })

        return ref_points

    def __points_for_powerlines_transnet(self, powerline_ids):
        query = text("""
            SELECT ST_X(geom) AS p_x, ST_Y(geom) AS p_y, id
            FROM (
              SELECT (ST_DumpPoints(g.geom)).*, g.id
              FROM(
                SELECT geom, id FROM transnet_powerline WHERE id IN :powerline_ids
              ) AS g
            ) j;
         """)
        point_rows = db.engine.execute(query, powerline_ids=tuple(powerline_ids))
        ref_points = []
        for row in point_rows:
            ref_points.append({
                'latlng': [row['p_x'], row['p_y']],
                'powerline_id': row['id']
            })

        return ref_points

    def __points_with_osmids_transnet(self, osmids):
        query = text("""
            SELECT p.id AS p_id, ST_X(p.geom) AS p_x, ST_Y(p.geom) AS p_y,
                    p.tags AS p_prop
            FROM transnet_station p
            WHERE p.osm_id IN :osm_ids
        """)
        point_rows = db.engine.execute(query, osm_ids=tuple(osmids))
        ref_points = []
        for row in point_rows:
            ref_points.append({
                'id': row['p_id'],
                'latlng': [row['p_x'], row['p_y']],
                'properties': row['p_prop']
            })

        return ref_points
