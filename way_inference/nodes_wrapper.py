class NodesWrapper:
    bounds = []
    cur = None

    def __init__(self, sql_cursor, bounds):
        self.bounds = bounds
        self.cur = sql_cursor

    def get_nodes_osmids_in_cluster(self, cluster_geom_text):
        self.cur.execute(self._node_osmids_in_cluster_query(), [
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

    def get_closest_nodes_to(self, for_node_osmid, among_osm_ids):
        fetch_closest_query = '''
            WITH current_point AS (
                SELECT id, ST_AsText(geom) AS geom FROM point
                WHERE (properties->>'osmid') = %s
            )
            SELECT point.id, point.properties->>'osmid',
                    ST_Distance(
                        ST_GeomFromText(current_point.geom),
                        point.geom
                    )
                FROM point, current_point
                WHERE ST_Distance(ST_GeomFromText(current_point.geom), point.geom) > 0.0004
                    AND ST_Distance(ST_GeomFromText(current_point.geom), point.geom) < 0.09
                    AND properties->>'osmid' IN %s
                ORDER BY ST_Distance(ST_GeomFromText(current_point.geom), point.geom) ASC
                LIMIT 1
        '''
        self.cur.execute(fetch_closest_query, [
            for_node_osmid,
            among_osm_ids
        ])
        return self.cur.fetchall()

    def get_farthest_nodes_among_nodes(self, among_osm_ids):
        farthest_nodes_query = '''
            WITH point_ids AS (
                SELECT id FROM point
                WHERE (point.properties->>'osmid') IN %s
            )
            SELECT a.properties->>'osmid',
                    b.properties->>'osmid',
                    st_distance(a.geom, b.geom)
            FROM point a, point b
            WHERE a.id IN (SELECT id FROM point_ids)
                    AND b.id IN (SELECT id FROM point_ids)
                    AND a.id != b.id
            ORDER BY st_distance(a.geom, b.geom) DESC
            LIMIT 1;
        '''
        self.cur.execute(farthest_nodes_query, [
            tuple(among_osm_ids)
        ])
        return self.cur.fetchone()

    def _node_osmids_in_cluster_query(self):
        return '''
            SELECT DISTINCT properties->>'osmid' FROM point
            WHERE ST_Intersects(
                    ST_CollectionExtract(%s, 1),
                    point.geom
                  )
                AND properties->'tags'->>'power'='tower'
                AND ST_Intersects(
                        ST_MakeEnvelope(%s, %s, %s, %s),
                        point.geom
                    );
        '''
