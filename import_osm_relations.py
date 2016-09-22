from imposm.parser import OSMParser
import psycopg2
import json
import sys

'''
WARNING: This could be a very memory intense script. The variables can grow
huge depending on the size of imports. You are adviced to import in smaller
sizes. We advice you run this with on the +.pbf+ files that have only
relations related data. Use the command line tool osmosis
(http://wiki.openstreetmap.org/wiki/Osmosis) to filter out the file to
contain only power relations and run this script on that
result file. Below is an example script on how to run osmosis.

  osmosis --read-pbf file=bayern-latest.osm.pbf --tag-filter accept-relations --used-way --used-node --buffer --write-pbf file=bayern-latest-relations.pbf

NOTE: This script only imports points and powerlines that are related to a
relation. To import other generic points and powerlines, use the usual
+import_osm_data.py+ script.

This is what we do here:
    1. Save all the points from the file to a temporary table, +temp_points+.
        We user +coords_callback+ of imposm.parser.

    2. Update the points in +temp_points+ with their tags.
        Here, we use +nodes_callback+ of imposm.parser.

        We do it in two steps because imposm.parser's +nodes_callback+ will return
        only nodes that have tags. If we wanna import all the points in the
        file, we should use +coords_callback+ which gives all nodes including
        those that don't have tags.

    3. Read and save relations to +power_relations+ table.
        Relations have members which can be ways or nodes or both.

        We save the relation between the power_relation records and the members
        in a join table +power_relation_members+.
        So, in this same step, also add a record in the +power_relation_members+
        join table with +member_id+ as the id of the members in their respective
        tables. It might b the case that we don't find the member in our database
        yet. In such case, we add +member_id+ as or NULL and update the
        +member_id+ from the later steps when we have the records imported.

    4. Start importing the ways and update +power_relation_members+ creating
       the relationship between ways and relations.
        The ways are structured in osm such that they have the osmid of all the
        points that form them. These points would have been imported in the
        step 1. While importing a way, we take it's points' osmids and query the
        +temp_points+ table to get their coordinates(latitude and longitude).
        Using these coordinates, we generate the linestring for this way and
        save it as +geom+ in the +powerline+ table which holds the records for
        these ways.

        While importing the ways, if we encounter a way whose osmid is
        found in the +power_relation_members.member_osmid+, we will update
        +power_relation_members.member_id+ to this way record's id to maintain
        a foreignkey relation.

    5. Find and update missing node member's relations in
       +power_relation_members+ table.
        Fetch the points from +temp_points+ that has osmid as member_osm_id
        from the +power_relation_members+ table and move them to actual +point+
        table. Get the id of this point from the +point+ table and
        update +power_relation_members.memeber_id+ for a foreignkey relation.

    6. Clean up the database.
        If you have any records in +temp_points+ they can be deleted.

    After all these steps, ideally, you shouldn't have any record in the
    +power_relation_members+ join table that has the +member_id+ value
    0 or NULL.
'''

try:
    conn = psycopg2.connect("dbname='gis' user='postgres' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")

class PointImporter(object):

    def perform(self, coords):
        for osmid, lon, lat in coords:
            print ".",

            query = "INSERT INTO temp_points(geom, properties, revised, approved) "\
                "VALUES(%s, %s, TRUE, TRUE)"
            query_values = (
                "POINT({} {})".format(lat, lon),
                json.dumps({ 'tags' : None , 'osmid' : osmid})
            )

            cur.execute(query, query_values)

class PowerStationImporter(object):

    def perform(self, nodes):
        for osmid, tags, coords in nodes:
            print ".",

            query = "UPDATE temp_points SET (geom, properties, revised, approved) "\
                "= (%s, %s, TRUE, TRUE) "\
                "WHERE properties->>'osmid' = %s"
            query_values = (
                "POINT({} {})".format(coords[1], coords[0]),
                json.dumps({ 'tags' : tags , 'osmid' : osmid}),
                str(osmid)
            )

            cur.execute(query, query_values)

class PowerlineImporter(object):

    def perform(self, ways):

        # For every way, check:
        #   if it is a member of any relation
        #       then insert the way
        #       update the power_relations with the way's id.
        for osmid, tags, refs in ways:
            print ".",

            # check if it is a member of atleast one relation:
            is_member_query = "SELECT id FROM power_relation_members "\
                "WHERE member_osm_id = %s "\
                    "AND member_type = %s "\
                    "AND (member_id = 0 OR member_id is NULL)"
            cur.execute(is_member_query, [str(osmid), 'way'])
            join_table_row = cur.fetchone()

            if join_table_row is not None:
                join_table_row_id = join_table_row[0]

                # get the points for the way
                nodes = []
                flag = False
                for ref in refs:
                    query = "SELECT ST_X(geom), ST_Y(geom) FROM temp_points "\
                        "WHERE properties->>'osmid' = %s"
                    cur.execute(query, [str(ref)] )
                    node = cur.fetchone()
                    if node is None:
                        print("\nMissing point {0} for powerling {1}".format(
                            str(ref),
                            osmid
                        ))
                        flag = True
                    else:
                        nodes.append(node)

                # skip this powerline if a point is missing in the database.
                if flag:
                    print("\nOne or more Points missing for line %s" % str(osmid))
                    continue

                if len(nodes) < 2:
                    print("\nLess than 2 points for line, skipping %s" % str(osmid))
                    continue

                linestring = ""
                for node in nodes:
                    linestring += "{} {},".format(node[0], node[1])
                linestring = linestring[:-1]

                is_in_powerline_query = "SELECT id, geom FROM powerline "\
                    "WHERE geom = %s"
                cur.execute(is_in_powerline_query, [
                    'LINESTRING({})'.format(linestring)
                ])
                powerline_record = cur.fetchone()
                if powerline_record is not None:
                    # Powerline already exists in the database. Take its id and
                    #   update the join table.
                    powerline_record_id = powerline_record[0]

                    join_table_update_query = "UPDATE power_relation_members "\
                        "SET member_id = %s "\
                        "WHERE member_osm_id = %s"

                    cur.execute(join_table_update_query, [
                        powerline_record_id,
                        str(osmid)
                    ])
                else:
                    query = "INSERT INTO powerline(geom, properties) VALUES(%s, %s)"
                    query_values = [
                        'LINESTRING({})'.format(linestring),
                        json.dumps({ "tags": tags, "refs": refs })
                    ]
                    cur.execute(query, query_values)

                    # TODO: Don't use +currval+
                    join_table_update_query = "UPDATE power_relation_members "\
                        "SET member_id = currval('powerline_id_seq') "\
                        "WHERE member_osm_id = %s"
                    cur.execute(join_table_update_query, [str(osmid)])
            else:
                print("\nHaven't found relation for powerline - osmid %s" % osmid)

class RelationsImporter(object):

    def perform(self, relations):
        for osmid, tags, members in relations:
            should_insert_relation = False

            if ('power' in tags) or ('power' in tags.values()):
                # Check if it is already imported
                is_already_imported_query = "SELECT id from power_relations "\
                    "WHERE properties->>'osmid' = %s"
                cur.execute(is_already_imported_query, [str(osmid)])

                if cur.fetchone() is not None:
                    should_insert_relation = False
                else:
                    should_insert_relation = True

            if should_insert_relation:
                print ".",

                relation_insert_query = "INSERT INTO power_relations(properties)"\
                    " VALUES (%s)"
                cur.execute(relation_insert_query, [
                    json.dumps({"tags": tags, "osmid": osmid})
                ])

                for member_osm_id, kind, role in members:
                    # TODO: Check if the member already exist and add relation
                    #       straight away. We check for nodes but ways in
                    #       the table +powerline+ doesn't have any osmid stored.
                    #       Once the osmid is made to be stored for them as
                    #       well, we include that logic too.
                    member_id = 0

                    if kind == 'node':
                        cur.execute(
                            "SELECT id FROM point WHERE "\
                                "properties->>'osmid' = %s",
                            [str(member_osm_id)]
                        )
                        member = cur.fetchone()
                        if member is not None:
                            member_id = member[0]


                    polymorphic_query = "INSERT INTO power_relation_members"\
                        "(power_relation_id, member_id, "\
                        "member_osm_id, member_type, member_role) "\
                        "VALUES (currval('power_relations_id_seq'), %s, %s, %s, %s)"

                    cur.execute(polymorphic_query, [
                        member_id, member_osm_id, kind, role
                    ])

all_points_importer = PointImporter()
power_station_importer = PowerStationImporter()
powerline_importer = PowerlineImporter()
relations_importer = RelationsImporter()

print("\nImporting the Points to temp_points: ")
p = OSMParser(concurrency=4, coords_callback=all_points_importer.perform )
p.parse(sys.argv[1])
conn.commit()

print("\nImporting the tags for Points that are in temp_points:")
p = OSMParser(concurrency=4, nodes_callback=power_station_importer.perform )
p.parse(sys.argv[1])
conn.commit()

print("\nImporting the Relations to power_relations and power_relation_members:")
p = OSMParser(concurrency=4, relations_callback=relations_importer.perform )
p.parse(sys.argv[1])
conn.commit()

print("\nImporting the Powerlines to +powerline+ and adding association with "
        + "power_relations:")
p = OSMParser(concurrency=4, ways_callback=powerline_importer.perform)
p.parse(sys.argv[1])
conn.commit()

print("\nAdding Point-to-Relation assosication and copying those points from "
      + "temp_points to actual point table:")
# find missing node relations from temp_points and update power_relations table

# get the OSM ids of the nodes that are as power_relation_members.
# There are some cases where the nodes are missing in the OSM data but relations
# are marked with those nodes anyway. Having JOIN in the query below makes sure
# we bother only those that are present.
nodes_osmids_query = """SELECT pr.id, pr.member_osm_id FROM
                            power_relation_members pr
                        JOIN temp_points tp
                            ON pr.member_osm_id = tp.properties->>'osmid'
                        WHERE (pr.member_id = 0 OR pr.member_id is NULL)
                            AND pr.member_type='node';"""
cur.execute(nodes_osmids_query)
rows = cur.fetchall()
for row in rows:
    print ".",
    relation_id = row[0]
    node_osmid = row[1]

    query = """ WITH point_record AS (
                    INSERT INTO point (geom, properties, revised, approved)
                    SELECT geom, properties, revised, approved
                        FROM temp_points
                        WHERE properties->>'osmid' = %s
                    RETURNING id
                )
                UPDATE power_relation_members
                SET member_id = (
                    SELECT id FROM point_record
                )
                WHERE member_osm_id = %s """

    cur.execute(query, [str(node_osmid), str(node_osmid)])

conn.commit()

# Delete the temp_points's records.
print("\nDeleting temp_points table:")
truncate_temp_points_query = "TRUNCATE temp_points;"
cur.execute(truncate_temp_points_query)
conn.commit()
