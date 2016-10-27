$(document).ready(function() {
    registerHandleBarHelpers();
    var osmTile = MapHelpers.getOsmTile();
    var satelliteTile = MapHelpers.getSatelliteTile();

    var pgisMap = new PgisSubmissionGalleryMap();
    pgisMap.createMap(osmTile);

    var map = pgisMap.map;

    var baseMaps = {
        "Satellite View": satelliteTile,
        "Topological View": osmTile
    };

    pgisMap.addBaseMaps(baseMaps);

    pgisMap.addMarkerLayer({
        name: 'markers',
        layer: new L.MarkerClusterGroup()
    });
    // pgisMap.addMarkerLayer({
    //     name: 'clusterGroup',
    //     layer: new L.LayerGroup()
    // });
    // pgisMap.addMarkerLayer({
    //     name: 'powerlinesLayerGroup',
    //     layer: new L.LayerGroup()
    // });

    var _pgisMap = pgisMap;

    pgisMap.baseMapDataLoader = function() {
        MapDataLoader.loadBaseMapDataForMapFragment(
            pgisMap,
            this.markerLayers.markers,
            this.galleryContainer
        );
    };

    pgisMap.baseMapDataLoader();

    window.pgisMap = pgisMap;
});
