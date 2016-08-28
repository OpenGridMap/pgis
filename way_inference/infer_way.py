import psycopg2
import json
import sys
import ast
from cluster_wrapper import ClusterWrapper
from nodes_wrapper import NodesWrapper

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

bounds = [28.212890625, -1.8261677821806805, 33.486328125, 0.8349313860427184]
clusterWrapper = ClusterWrapper(cur, bounds)
clusters = clusterWrapper.getClusters()

for cluster in clusters:
    nodes_osmids = NodesWrapper(cur, bounds).get_nodes_osmids_in_cluster(cluster[0])

# processing_node = "3212196097"
processing_node = "2043615536"
processed_nodes = []
processed_nodes.append(processing_node)

is_complete = False

while is_complete == False:
    # print(processed_nodes)
    # print "processing - ",
    # print(processing_node)
    closest_nodes = NodesWrapper(cur, []).get_closest_nodes_to(
        processing_node,
        tuple(set(tuple(processed_nodes)) ^ set(nodes_osmids))
    )
    closest_node = None
    print(closest_nodes)

    if len(closest_nodes) > 0:
        closest_node = closest_nodes[0] # There are already ordered by distance

    if closest_node is not None and len(closest_node) > 0:
        print "Closest is - ",
        print(closest_node[1])
        processing_node = closest_node[1]
        processed_nodes.append(processing_node)
    else:
        print("\n*********** IS COMPLETE **************\n")
        is_complete = True

print(processed_nodes)
for node_osmid in processed_nodes:
    print("node(%s);" % node_osmid)
