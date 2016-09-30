from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import json

# Presenter logic for Relations (plural).
class RelationsPresenter:
    def __init__(self, relations):
        self.relations = relations

    def as_xml_element(self):
        relations_elem = Element('relations')

        for relation_id, relation in self.relations.items():
            relation_elem = SubElement(relations_elem, 'relation', {
                'id': str(relation['id']),
                'osmid': str(relation['properties']['osmid']),
            })
            self.__buildXmlSubElementForTags(
                relation['properties']['tags'],
                relation_elem
            )

            points_elem = SubElement(relation_elem, 'points')
            for point in relation['points']:
                point_elem = SubElement(points_elem, 'point', {
                    'lat': str(point['latlng'][0]),
                    'lng': str(point['latlng'][1]),
                    'osmid': str(point['properties']['osmid']),
                    'id': str(point['id'])
                })
                self.__buildXmlSubElementForTags(
                    point['properties']['tags'],
                    point_elem
                )

            powerlines_elem = SubElement(relation_elem, 'powerlines')
            for powerline in relation['powerlines']:
                powerline_elem = SubElement(powerlines_elem, 'powerline', {
                    'id': str(powerline['id'])
                })

                for latlng in powerline['latlngs']:
                    latlng_elem = SubElement(powerline_elem, 'point', {
                        'lat': str(latlng[0]),
                        'lng': str(latlng[1])
                    })

                self.__buildXmlSubElementForTags(
                    powerline['properties']['tags'],
                    powerline_elem
                )

        return tostring(relations_elem)

    def __buildXmlSubElementForTags(self, tags, parent_xml_element):
        for tag, value in tags.items(): # tag.items() because tags is a dict
            tag_elem = SubElement(parent_xml_element, 'tag', {
                'key': tag,
                'value': str(value)
            })
