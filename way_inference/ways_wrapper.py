import json

class WaysWrapper:
    bounds = []
    cur = None

    def __init__(self, sql_cur, bounds):
        self.cur = sql_cur
        self.bounds = bounds

    def is_node_in_any_polygon(self, node_osmid):
        query = '''
            WITH node AS (
                SELECT geom FROM point WHERE properties->>'osmid' = %s
            )
            SELECT powerline.id
            FROM powerline, node
            WHERE ST_Contains(ST_MakePolygon(powerline.geom), node.geom)
                AND ST_IsClosed(powerline.geom)
            LIMIT 1
        '''
        self.cur.execute(query, [str(node_osmid)])
        powerline = self.cur.fetchone()
        if powerline is not None:
            return True
        else:
            return False

    def save_to_database(self, nodes_osmids, inferrence_notes):
        nodes = []
        flag = False
        for node_osmid in nodes_osmids:
            query = "SELECT ST_X(geom), ST_Y(geom) FROM point WHERE properties->>'osmid' = %s"
            self.cur.execute(query, [str(node_osmid)] )
            node = self.cur.fetchone()
            if node is None:
                flag = True
            else:
                nodes.append(node)

        if flag:
            return None

        if len(nodes) < 2:
            return None

        linestring = ""
        for node in nodes:
            linestring += "{} {},".format(node[0], node[1])

        linestring = linestring[:-1]
        print("Saving powerline to database")
        query = "INSERT INTO inferred_powerlines(geom, properties) VALUES(%s, %s)"
        self.cur.execute(query, [
            'LINESTRING({})'.format(linestring),
            json.dumps({ "tags": {"inferrence": inferrence_notes}, "refs": nodes_osmids, })
        ])

