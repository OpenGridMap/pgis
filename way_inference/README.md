# Way Inference

# How does it work?

The idea was to take basic simple methods and make them work in co-ordination and show methods for way inference covering possible scenarios.
> These scripts at the moment can't perform very good inferrence. This is more like, prooving the possiblity.


## Basic script

Takes in boundaries to run inferrence on that region of the map.
Gets clusters of point (discussed [here](#clustering)) and loops over each cluster. Each cluster is possibly a powerline.
For each cluster
* Start inferrence with a point the cluster.
* Fetch the database and choose a possible point.
 * Here we have different options on how to choose a next point. Some are even ignored during this process (discussed later in this document).
* Once we have gone though all the points, we will save the points as a line into the database.
* Alternative to the above point, if we encounter a point that meets a polygon (building), we assume its the end of the line and save the line to database.
We will continue freshly with the remaining point from the cluster as new a new cluster.

As simple as that!

## Clustering

Everything basically starts with [clustering](#clustering) in the way inference.
Given a boundary, we take clusters of points in that region from our database.
We take the points that are not marked as substations or stations or something similar.
We cluster points based on the distance between them.
For powerlines (at least) for those we had in the database, we calculated (using `../estimate_power_pole_distance.py` script) the average maximum distance between two points in a powerline is around 0.1 in postGIS distance units (projected units based on spatial ref - [See more](http://postgis.net/docs/ST_Distance.html)).
So, we cluster points that are in that distance of each other (at least with another point in that cluster).
You could see the `ClusterWrapper` for the code related to this.

## Choosing a point to start with

Within a cluster, we choose the points based on different methods.

### Farthest points

By default, we choose one of the two farthest points.
The distances are calculated and farthest points are fetched from SQL for performance leveraging the [postGIS](http://postgis.net) functions.
The script then takes one of those points as a starting point.

### Points on a substation
**Optional**

Some polygons are tagged with `power: substation` in the OpenStreetMaps data to mark substations.
If the option to select such points in the script, the script fetches points (from the cluster) that intersects/within such polygons.
This again uses the postGIS functions and such points are fecthed using SQL queries.
The script then takes one of those points as a starting point.
If no such points are found, falls back to using **Farthest points**


# Requirements
* Postgres with [postGIS](http://postgis.net) Version 2.2
* Python 2.7
