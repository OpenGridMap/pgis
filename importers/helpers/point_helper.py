# --- IMPORTANT ---
# Remember, all these methods require conn.commit() to be called on the
#   database connector after they are run. It is left to the caller of these
#   methods to do that!

import json

class PointHelper:
    sql_cur = None

    def __init__(self, sql_cursor):
        self.sql_cur = sql_cursor

    def insert_with_values(self, lat, lon, osmid, tags):
        # insert only if not exists already.
        query = '''
            INSERT INTO point(
                geom, properties, revised, approved
            )
            SELECT %s, %s, TRUE, TRUE
            WHERE
                NOT EXISTS (
                    SELECT id FROM point WHERE properties->>'osmid' = %s
                )
        '''
        query_values = (
            "POINT({} {})".format(lat, lon),
            json.dumps({ 'tags' : tags , 'osmid' : osmid}),
            str(osmid)
        )

        self.sql_cur.execute(query, query_values)

    def find_with_osmid(self, osmid):
        query = '''
            SELECT ST_X(geom), ST_Y(geom)
            FROM point
            WHERE properties->>'osmid' = %s
        '''
        self.sql_cur.execute(query, [str(osmid)] )
        node = self.sql_cur.fetchone()
        return node
