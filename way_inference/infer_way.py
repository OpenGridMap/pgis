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

nodesWrapper = NodesWrapper(cur, bounds)
clustersWrapper = ClusterWrapper(cur, bounds)
waysWrapper = WaysWrapper(cur, bounds)

clusters = clustersWrapper.getClusters()

for cluster in clusters:
    nodes_osmids = nodesWrapper.get_nodes_osmids_in_cluster(cluster[0])
print(nodes_osmids)


farthest_nodes = nodesWrapper.get_farthest_nodes_among_nodes(nodes_osmids)
print(farthest_nodes)

# Start processing with one of the farthest nodes
processing_node = farthest_nodes[0]

processed_nodes = []
ignored_nodes = [] # nodes are ignored if there are too close to a node

processed_nodes.append(processing_node)

is_complete = False

while is_complete == False:
    # procesed nodes minus the all nodes
    unprocessed_nodes = tuple(set(tuple(processed_nodes)) ^ set(nodes_osmids))

    # unprocessed nodes minus the ignored node.
    unprocessed_nodes = tuple(set(unprocessed_nodes) ^ set(tuple(ignored_nodes)))

    closest_node = None


    if len(unprocessed_nodes) > 0:
        nodes_around = nodesWrapper.get_closest_nodes_to(
            processing_node,
            unprocessed_nodes
        )

        ignored_nodes = ignored_nodes + nodes_around['too_close_node_osmids']
        closest_node = nodes_around['closest_node_osmid']
    else:
        is_complete = True
        continue

    if closest_node is not None:
        print "Closest is - ",
        print(closest_node)
        processing_node = closest_node
        processed_nodes.append(processing_node)

        # if the node that is just processed in
        if waysWrapper.is_node_in_any_polygon(processing_node):
            is_complete = True

    else:
        print("\n*********** IS COMPLETE **************\n")
        is_complete = True

print(processed_nodes)
for node_osmid in processed_nodes:
    print("node(%s);" % node_osmid)

waysWrapper.save_to_database(processed_nodes)
conn.commit()
