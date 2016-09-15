# Way Inference

# How does it work?

The idea was to take basic simple methods and make them work in co-ordination and show methods for way inference covering possible scenarios.
> These scripts at the moment can't perform very good inferrence. This is more like, prooving the possiblity.


## Basic script

Takes in boundaries to run inferrence on that region of the map.
Gets clusters of point (discussed [here](#clustering)) and loops over each cluster. Each cluster is possibly a powerline.
For each cluster
* Start inferrence with a point the cluster. How we pick a point to start with is discussed [Here](#choosing-a-point-to-start-with)
* Fetch the database and choose a [possible next point](#choosing-a-possible-next-point).
 * Here we have different options on how to choose a next point. Some are even ignored during this process (discussed [here](#choosing-a-possible-next-point)).
* Once we have gone though all the points, we will save the points as a line into the database.
* Alternative to the above point, if we encounter a point that meets a polygon (building), we assume its the end of the line and save the line to database.
We will continue freshly with the remaining point from the cluster as new a new cluster.

As simple as that!

## Clustering

Everything basically starts with clustering.
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
Also, lines that are taggest with `power: line` but are closed are also usually substations.
If the option to select such points in the script, the script fetches points (from the cluster) that intersects/within such polygons.
This again uses the postGIS functions and such points are fecthed using SQL queries.
The script then takes one of those points as a starting point.
If no such points are found, falls back to using **Farthest points**

## Choosing a possible next point

This is one of the critical steps which would make a difference on how the lines are inferred.
A possible next point from a point is done based on different variables.
We have tested these variables seperately. They cannot all work together.
However, a few of them can work together.

### Closest point in a ring

By default, we choose the next closest point in a ring.
Its highly possible that a point has points that are too close (in case of parallelly running powerlines).
We don't want to join those _too-close_ points.
Similarly, there are always points around a point that are too far.
We used the `../estimate_power_pole_distance.py` script to find the average minimum and maximum distance between adjacent points among the powerlines in our database.
Using these minimum and maximum distance, we set the variables in the `NodeWrapper` and form an SQL query to fetch points within the ring with inner and outer radii as minimum and maximum distances respectively.
From these closest points we take the most closest point.

**Issues:**
* Crossing powerlines: There usually are powerlines crossing each other and this method might fail by picking a point in supposed to be the other powerline.
* Lines joining at a substations: Powerlines usually join at a substation and this method might fail by picking points from other powerlines, similar to the _Crossing powerlines_ issue.
* Parallel lines: Powerlines tend to run parallel for quite some distances from a substation, such parallel lines are failed to be inferred correctly. It forms a zig-zag pattern by joining points from the possible two line alternatively.

**Works best for:**
* Lone powerlines: Powerlines that run idependantly without any intersections and parallel neighbours.

### Point causing less angle of deviation

Not default. Set by setting the variable `is_less_deviating_point_preferred` to `True`.

While building a line, this method will choose a point that will deviate a line with a lesser angle than all other points that are around it within a maximum distance of 0.008 units.
This maximum distance is needed so that, too far away nodes are not taken into consideration as quite often the farthest nodes create less deviation angle.
From a given point, we gather the possible angle formed by all the points within the maximum distance.
We will then ceil these angles to the closest 5th multiple and round up the distances upto third decimal point.
We sort these nodes by angle and then by distance so that all the nodes that are forming noticeable deviation (5 degree angle) form a group.
We will then choose the closest node from the group that forms the least deviation.

The varibales that control angles' ceiling multiple, distance roundup decimal point and maximum distance for point to be considered in angle deviation calculation are within the `NodesWrapper` class.

**Issues:**
* Lines joining at a substation: Such lines usually take sharp turns at substations but points from neighbouring lines might show less deviations.

**Works better for:**
* Parallel lines
* Crossing powerlines


## Varibles that can work together
* Farthest points, Points on a substation, Next Closest within the ring, Point causing less deviation.

# Requirements
* Postgres with [postGIS](http://postgis.net) Version 2.2
* Python 2.7
