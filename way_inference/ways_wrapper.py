import json

class WaysWrapper:

    def __init__(self, sql_cur):
        self.cur = sql_cur

    def save_to_database(self, nodes_osmids):
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
        print(nodes)
        for node in nodes:
            linestring += "{} {},".format(node[0], node[1])

        linestring = linestring[:-1]
        print("INSERTING {}".format(linestring))
        query = "INSERT INTO inferred_powerlines(geom, properties) VALUES(%s, %s)"
        self.cur.execute(query, [
            'LINESTRING({})'.format(linestring),
            json.dumps({ "tags": {}, "refs": nodes_osmids })
        ])

