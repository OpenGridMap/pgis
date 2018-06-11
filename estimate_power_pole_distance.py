import psycopg2
import json
import sys
import ast
import numpy as np
import scipy.stats as stats
import pylab as pl

try:
    conn = psycopg2.connect("dbname='gis' user='Munna' host='localhost' password=''")
    cur = conn.cursor()
except:
    print("I am unable to connect to the database")

min_distances = []
max_distances = []

get_powerlines_query = "SELECT id as id, properties->>'refs' as ref FROM powerline LIMIT 10"
cur.execute(get_powerlines_query)
powerlines = cur.fetchall()
for powerline in powerlines:
    nodes_osmids = ast.literal_eval(powerline[1])
    nodes_osmids = tuple([str(i) for i in nodes_osmids])
    nodes_count_query = "SELECT count(DISTINCT id) FROM point WHERE properties->>'osmid' IN %s"
    cur.execute(nodes_count_query, (nodes_osmids, ))
    nodes_count = cur.fetchone()
    # check if we have all the nodes for a powerline in our database
    if nodes_count[0] == len(nodes_osmids):
        nodes_distances_query = '''SELECT MIN(ST_Distance(a.geom, b.geom)),
                                MAX(ST_Distance(a.geom, b.geom))
                            FROM
                            point a,
                            point b
                            WHERE a.id IN (SELECT DISTINCT id FROM point where properties->>'osmid' in %s)
                                AND b.id IN (SELECT DISTINCT id FROM point where properties->>'osmid' in %s)
                                AND a.id != b.id'''
        cur.execute(nodes_distances_query, (nodes_osmids, nodes_osmids, ))
        distances = cur.fetchone()
        print(distances)
        min_distances.append(distances[0])
        max_distances.append(distances[1])

print("Average minimum distance: ", )
print(reduce(lambda x, y: x + y, min_distances) / len(min_distances))
print("Average maximum distance: ", )
print(reduce(lambda x, y: x + y, max_distances) / len(max_distances))

# h = sorted(min_distances)

# fit = stats.norm.pdf(h, np.mean(h), np.std(h))  #this is a fitting indeed

# f = pl.figure()
# pl.plot(h,fit,'-o')
# pl.hist(h,normed=True)      #use this to draw histogram of your data
# f.savefig('min.pdf')

# h = sorted(max_distances)

# fit = stats.norm.pdf(h, np.mean(h), np.std(h))  #this is a fitting indeed

# f = pl.figure()
# pl.plot(h,fit,'-o')
# pl.hist(h,normed=True)      #use this to draw histogram of your data
# f.savefig('max.pdf')
