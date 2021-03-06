## Filters

The filters in this directory are bash scripts that help you filter the
OSM data files that you would get from
[http://download.geofabrik.de](http://download.geofabrik.de).

These scripts uses [Osmosis](http://wiki.openstreetmap.org/wiki/Osmosis) tool
to perform the filtering. Install it before running any of these scripts.

All the OSM data files that are read by this script are expected to be of
[.pbf format](http://wiki.openstreetmap.org/wiki/PBF_Format). The filtered files
generated by these script will be of the same format.

### Power nodes and ways (`./power_nodes_and_way`)

The file will filter a given OSM data file to contain
* Nodes that have the tag `power=*`.
* Ways that have the tag `power=*`.
* Nodes that are part of filtered ways even if they are **not** tagged with `power=*`.

##### Usage:

````console
# from within the scripts directory
./power_nodes_and_way ~/Downloads/bayern-latest.osm.pbf
````

The filtered file will be generated into the same directory as the source file
with the name appended with `.filtered.power.nodes_and_ways.pbf`. So for the
example above, the filtered file would be
`~/Downloads/bayern-latest.osm.pbf.filtered.power.nodes_and_ways.pbf`
