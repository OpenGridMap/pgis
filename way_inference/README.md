## Way Inference

### How does it work?

The idea was to take basic simple methods and make them work in co-ordination and show methods for way inference covering possible scenarios.
> These scripts at the moment can't perform very good inferrence. This is more like, prooving the possiblity.


#### Basic script.

Takes in boundaries to run inferrence on that region of the map.
Gets clusters of point (discussed [here](#clustering)) and loops over each cluster. Each cluster is possibly a powerline.
For each cluster
* Start inferrence with a point the cluster.
* Fetch the database and choose a possible point.
 * Here we have different options on how to choose a next point. Some are even ignored during this process (discussed later in this document).
* Once we have gone though all the points, we will save the points as a line into the database.

As simple as that!

##### Clustering

Everything basically starts with [clustering](#clustering) in the way inference.
Given a boundary, we take clusters of points in that region from our database.
We take the points that are not marked as substations or stations or something similar.
We cluster points based on the distance between them.
For powerlines (at least) for those we had in the database, we calculated (using `../estimate_power_pole_distance.py` script) the average maximum distance between two points in a powerline is around 0.1 in postGIS distance units (projected units based on spatial ref - [See more](http://postgis.net/docs/ST_Distance.html)).
So, we cluster points that are in that distance of each other (at least with another point in that cluster).
You could see the `ClusterWrapper` for the code related to this.

##### Choosing a point to start with
Lorem ipsum dolor sit amet, pro stet iisque commune no, vix tibique inimicus ut. Quando mandamus eu nec. Sed facilisi vituperata ea. Sea mundi choro dicam ad.

Ludus integre menandri eu sea, ex pri dicam electram. Nibh homero ocurreret in ius. Et sit alia feugait noluisse, viderer dolorem voluptatum eum in. Vis purto noster virtute te, dicit populo ad nec, sed in purto dicta liber. Vel tale ullum oratio ea, ius luptatum vivendum quaerendum an.

Sententiae delicatissimi ex vis, ea eos ferri torquatos appellantur. Lorem nostro philosophia cu sit, ne odio meliore vivendum mei, vidit impetus docendi ut his. Eu mel vitae congue pericula. Nam te cetero luptatum, no duo vero deterruisset. Vel dicat partiendo dissentiunt te.

In quot dicunt maiorum mel. Nominavi sensibus sit in, per purto feugait forensibus ea. Mel ne agam mutat molestie, cum probo ipsum accusamus ut. Soluta instructior in per, per ad causae ocurreret patrioque.

Nec vero iudicabit reprehendunt ne, has dolorum civibus electram et. His ea munere volumus accommodare, affert neglegentur te sit. Ad rebum consequat mel, et alii tritani per. Ne sit detracto mediocrem suscipiantur, civibus placerat consectetuer quo ei. Te everti persecuti eum, vis ne mutat errem. Pro tritani rationibus cu, virtute concludaturque mel an, et sit tota harum recusabo. Saepe maiorum atomorum qui eu.
