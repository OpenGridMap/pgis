import math
from decimal import *

class NodesWrapper:
    bounds = []
    cur = None
    closest_min_distance = 0.0004
    closest_max_distance = 0.09
    closest_max_distance_for_angles = 0.008# 0.0055 # tells to get angles for those only within that distance.
    parallel_line_nodes_max_distance = 0.0006
    angle_ceil_multiplier = 5

    def __init__(self, sql_cursor, bounds):
        self.bounds = bounds
        self.cur = sql_cursor

    def get_nodes_osmids_in_cluster(self, cluster_geom_text):
        query = '''
            SELECT DISTINCT properties->>'osmid' FROM point
            WHERE ST_Intersects(
                    ST_CollectionExtract(%s, 1),
                    point.geom
                  )
                AND properties->>'tags' LIKE '%%power%%'
                AND ST_Intersects(
                        ST_MakeEnvelope(%s, %s, %s, %s),
                        point.geom
                    );
        '''
        self.cur.execute(query, [
            cluster_geom_text,
            self.bounds[1],
            self.bounds[0],
            self.bounds[3],
            self.bounds[2]
        ])
        node_osmids_tuple = self.cur.fetchall()
        # Return an array instead of a tuple.
        def tmp(x): return x[0]
        return list(map(tmp, node_osmids_tuple))

    def get_closest_nodes_to(self, for_node_osmid, among_osm_ids,
                            previous_node_osmid=None):
        fetch_closest_query = '''
            WITH current_point AS (
                SELECT id, ST_AsText(geom) AS geom FROM point
                WHERE (properties->>'osmid') = %s
            )
            SELECT point.id, point.properties->>'osmid',
                    ST_Distance(
                        ST_GeomFromText(current_point.geom),
                        point.geom
                    ) as distance
                FROM point, current_point
                WHERE ST_Distance(ST_GeomFromText(current_point.geom), point.geom) < %s
                    AND ST_Distance(ST_GeomFromText(current_point.geom), point.geom) > 0
                    AND properties->>'osmid' IN %s
                ORDER BY ST_Distance(ST_GeomFromText(current_point.geom), point.geom) ASC
        '''
        self.cur.execute(fetch_closest_query, [
            for_node_osmid,
            self.closest_max_distance,
            among_osm_ids,
        ])
        closest_nodes = self.cur.fetchall()
        result = {
            'too_close_node_osmids': [],
            'possible_parallel_line_nodes': [],
            'closest_node_osmid': None,
            'angles': [] # contains tuple with (osmid, roundedup distance, ceiled angle)
        }

        for node in closest_nodes:
            if (node[2] < self.parallel_line_nodes_max_distance):
                result['possible_parallel_line_nodes'].append(node[1])

            if (previous_node_osmid is not None) and (node[2] <= self.closest_max_distance_for_angles):
                # Case to include angles formed.
                angle = self.get_deviation_angle(previous_node_osmid, for_node_osmid, node[1])
                if angle is not None:
                    angle = (int(math.ceil(angle/ Decimal(self.angle_ceil_multiplier))) * self.angle_ceil_multiplier)
                    rounded_up_distance = math.ceil(node[2] * 1000)/1000
                    node_dist_angle_tuple = (node[1], rounded_up_distance, angle)
                    result['angles'].append(node_dist_angle_tuple)


        for node in closest_nodes:
            if (node[2] < self.closest_min_distance):
                result['too_close_node_osmids'].append(node[1])
            else:
                result['closest_node_osmid'] = node[1]
                break;

        return result;

    def get_node_osmids_intersecting_polygons(self, among_osm_ids):
        query = '''
            SELECT point.properties->>'osmid'
            FROM point
            JOIN powerline
            ON ST_Contains(ST_MakePolygon(powerline.geom), point.geom)
                AND ST_IsClosed(powerline.geom)
                AND point.properties->>'osmid' IN %s
                AND ST_Intersects(
                    ST_MakeEnvelope(%s, %s, %s, %s),
                    powerline.geom
                )
        '''
        self.cur.execute(query, [
            tuple(among_osm_ids),
            self.bounds[1],
            self.bounds[0],
            self.bounds[3],
            self.bounds[2]
        ])
        return self.cur.fetchall()

    def get_farthest_nodes_in_cluster(self, cluster_geom_text):
        query = '''
            WITH farthest AS (
                SELECT ST_Distance(a.geom, b.geom) AS distance,
                    a.geom AS a_geom, b.geom AS b_geom FROM
                (SELECT (ST_DumpPoints(ST_ConvexHull(ST_GeomFromText(%s)))).geom) a,
                (SELECT (ST_DumpPoints(ST_ConvexHull(ST_GeomFromText(%s)))).geom) b
                ORDER BY ST_Distance(a.geom, b.geom) DESC
                LIMIT 1
            )
            SELECT a.properties->>'osmid',
                    b.properties->>'osmid',
                    farthest.distance
            FROM point a, point b, farthest
            WHERE a.geom = farthest.a_geom
                    AND b.geom = farthest.b_geom
            LIMIT 1;
        '''
        self.cur.execute(query, [cluster_geom_text, cluster_geom_text])
        return self.cur.fetchone()


    def get_farthest_nodes_among_nodes(self, among_osm_ids):
        # Using ST_ConvexHull for finding farthest nodes seems to be
        #   optimal.
        # Refer: http://gis.stackexchange.com/a/25078/80804
        query = '''
            WITH farthest AS (
                SELECT ST_Distance(a.geom, b.geom) AS distance,
                    a.geom AS a_geom, b.geom AS b_geom FROM
                (SELECT (ST_DumpPoints(ST_ConvexHull(ST_Collect(geom)))).geom FROM point WHERE properties->>'osmid' IN %s) a,
                (SELECT (ST_DumpPoints(ST_ConvexHull(ST_Collect(geom)))).geom FROM point WHERE properties->>'osmid' IN %s) b
                ORDER BY ST_Distance(a.geom, b.geom) DESC
                LIMIT 1
            )
            SELECT a.properties->>'osmid',
                    b.properties->>'osmid',
                    farthest.distance
            FROM point a, point b, farthest
            WHERE a.geom = farthest.a_geom
                    AND b.geom = farthest.b_geom
                    AND a.properties->>'osmid' IN %s
                    AND b.properties->>'osmid' IN %s
            LIMIT 1;
        '''
        self.cur.execute(query, [
            tuple(among_osm_ids),
            tuple(among_osm_ids),
            tuple(among_osm_ids),
            tuple(among_osm_ids)
        ])
        return self.cur.fetchone()

    def get_deviation_angle(self, point1, intersection, point2):
        # Returns the angle at which the line joining +intersection+ point
        # with +point2+ devitates the line formed by joining point1 to
        # intersection
        query = '''
        WITH
            point1 AS (SELECT geom FROM point WHERE properties->>'osmid' = %s),
            intersection AS (SELECT geom FROM point WHERE properties->>'osmid' = %s),
            point2 AS (SELECT geom FROM point WHERE properties->>'osmid' = %s)

        SELECT CASE WHEN deg_i21i > 180 THEN (360 - deg_i21i)
                     ELSE deg_i21i END
        FROM (
                SELECT
                    abs(round(degrees(
                        ST_Azimuth(
                            ST_Point(ST_y(intersection.geom), ST_x(intersection.geom)),
                            ST_Point(ST_y(point2.geom), ST_x(point2.geom))
                        ) -
                        ST_Azimuth (
                            ST_Point(ST_y(point1.geom), ST_x(point1.geom)),
                            ST_Point(ST_y(intersection.geom), ST_x(intersection.geom))
                        )
                     )::decimal, 2))
                     AS deg_i21i
                FROM point1, point2, intersection
            ) s
        '''
        self.cur.execute(query, [str(point1), str(intersection), str(point2)])
        row = self.cur.fetchone()
        return row[0]

