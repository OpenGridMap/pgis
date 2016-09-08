class ClusterWrapper:
    bounds = []
    cur = None

    def __init__(self, sql_cur, bounds):
        self.bounds = bounds
        self.cur = sql_cur

    def getClusters(self):
        self.cur.execute(
            self._clusters_query(),
            self._clusters_query_args()
        )
        print(self._clusters_query_args())
        return self.cur.fetchall()

    def _clusters_query(self):
        # TODO: Get only the points that are not part of a powerline
        clusters_query = """
            SELECT ST_AsText(unnest((ST_ClusterWithin(geom, 0.1))))
                AS cluster_geom
            FROM point
            WHERE ST_Intersects(
                    ST_MakeEnvelope(%s, %s, %s, %s),
                    geom
                  )
                  AND properties->>'tags' LIKE '%%power%%'
            """
        return clusters_query

    def _clusters_query_args(self):
        args = [self.bounds[1], self.bounds[0],
                self.bounds[3], self.bounds[2]]
        return args

