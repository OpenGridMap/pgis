import psycopg2
import json
import sys
import ast
from cluster_wrapper import ClusterWrapper
from nodes_wrapper import NodesWrapper
from ways_wrapper import WaysWrapper

try:
    conn = psycopg2.connect("dbname='gis' user='Munna' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")

nodes_osmids = (
'3212196101', '3212196097', '3212196093', '3212196089', '3212196086', '3212196083',
'3212196077', '3212196075', '3212196071', '3212196045', '3212196012', '3212195977',
'3212195974', '3212195967', '3212195960', '3212195952', '3212195947',
'3212195940', '3212195935', '3212195931', '3212195926', '3212195925',
'3212195924', '3212195923', '3212195917', '3212195908', '3212195898',
'3212195884', '3212195874', '3212195866', '3212195869', '3212195878',
'3212195882', '3212195889', '3212195895', '3212195893', '3212195896'
)
# bounds = [10.39529800415039, 4.050234320898018, 10.50516128540039, 4.109221809610561] # parallel lines
bounds = [15.496902465820312, -1.4843615162701949, 16.375808715820312, -1.0113763068489454] # the short line in the middle of africa

# bounds = [15.003890991210938, -4.800890838853971, 15.663070678710938, -4.137558228375503] # bigger africa
# bounds = [15.232973098754881, -4.554179759718965, 15.342836380004883, -4.495226724658142]
# bounds = [15.070838928222654, -4.89223025116464, 15.510292053222656, -4.656501822101158]
# bounds = [15.22255539894104, -4.743145262934742, 15.23628830909729, -4.735778370815115]
bounds = [14.515686035156248, -5.103254918829327, 16.27349853515625, -4.160158150193397] # Africa Mbanza
# bounds = [10.853462219238281, 49.238000036465465, 11.292915344238281, 49.392206057422044] # Nuremburg

# settings
is_less_deviating_point_preferred = True
prefer_nodes_from_substations = True

nodesWrapper = NodesWrapper(cur, bounds)
clustersWrapper = ClusterWrapper(cur, bounds)
waysWrapper = WaysWrapper(cur, bounds)

clusters = clustersWrapper.getClusters()

def infer_way_from_nodes(nodes_osmids, cluster_geom_text=None):

    processing_node = None

    if prefer_nodes_from_substations == True:
        nodes_on_polygons = nodesWrapper.get_node_osmids_intersecting_polygons(nodes_osmids)
        if len(nodes_on_polygons) > 0:
            processing_node = nodes_on_polygons[0][0]

    if processing_node is None:
        if cluster_geom_text is not None:
            farthest_nodes = nodesWrapper.get_farthest_nodes_in_cluster(cluster_geom_text)
        else:
            farthest_nodes = nodesWrapper.get_farthest_nodes_among_nodes(nodes_osmids)

        processing_node = farthest_nodes[0]

    processed_nodes = []
    ignored_nodes = [] # nodes are ignored if there are too close to a node
    possible_parallel_line_nodes = []

    processed_nodes.append(processing_node)

    is_complete = False

    while is_complete == False:
        # procesed nodes minus the all nodes
        unprocessed_nodes = tuple(set(nodes_osmids) - set(tuple(processed_nodes)))

        # unprocessed nodes minus the ignored node.
        unprocessed_nodes = tuple(set(unprocessed_nodes) - set(tuple(ignored_nodes)))

        closest_node = None

        if is_less_deviating_point_preferred and len(processed_nodes) > 1 and processing_node != processed_nodes[-2]:
            last_processed_node = processed_nodes[-2]
        else:
            last_processed_node = None

        if len(unprocessed_nodes) > 0:
            nodes_around = nodesWrapper.get_closest_nodes_to(
                processing_node,
                unprocessed_nodes,
                last_processed_node
            )

            ignored_nodes = ignored_nodes + nodes_around['too_close_node_osmids']
            possible_parallel_line_nodes = possible_parallel_line_nodes + nodes_around['possible_parallel_line_nodes']

            closest_node = None

            if is_less_deviating_point_preferred == True and len(nodes_around['angles']) > 0:
                sorted_nodes = sorted(
                    nodes_around['angles'],
                    key=lambda x: (x[2], x[1])
                ) # sort by angle and then distance

                print("From -> %s: %s" % (processing_node, sorted_nodes))

                if sorted_nodes[0][2] is not None: # angle could sometimes be none.
                    closest_node = sorted_nodes[0][0]

            if closest_node is None:
                closest_node = nodes_around['closest_node_osmid']
        else:
            is_complete = True
            continue

        if closest_node is not None:
            print ".",
            processing_node = closest_node
            processed_nodes.append(processing_node)

            # if the node that is just processed in any polygon.
            if waysWrapper.is_node_in_any_polygon(processing_node):
                is_complete = True
        else:
            print("\n*********** IS COMPLETE **************\n")
            is_complete = True

    if len(processed_nodes) < 1:
        # This means, we couldn't find any close nodes.
        # End the iteration of the cluster.
        return
    else:
        # print(processed_nodes)
        for node_osmid in processed_nodes:
            print("node(%s);" % node_osmid)

        inferrence_notes = {}
        if len(possible_parallel_line_nodes) >= (len(processed_nodes)/4):
            inferrence_notes = {
                'possible_error': True,
                'notes': 'Posisble paralle lines'
            }
        waysWrapper.save_to_database(processed_nodes, inferrence_notes)
        conn.commit()

        # all nodes minus the processed nodes
        unprocessed_nodes = tuple(set(nodes_osmids) - set(tuple(processed_nodes)))
        # unprocessed nodes minus the ignored node.
        unprocessed_nodes = tuple(set(unprocessed_nodes) - set(tuple(ignored_nodes)))

        if len(unprocessed_nodes) > 1:
            # There are more nodes to be processed in this cluster.
            infer_way_from_nodes(nodes_osmids=unprocessed_nodes)

for cluster in clusters:
    print("************ Processing New Cluster **************")
    nodes_osmids = nodesWrapper.get_nodes_osmids_in_cluster(cluster[0])
    if len(nodes_osmids) > 1:
        if prefer_nodes_from_substations:
            infer_way_from_nodes(nodes_osmids)
        else:
            infer_way_from_nodes(nodes_osmids, cluster[0])

    else:
        print("Not enough nodes in cluster! - SKIPPING")

