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
    // map.addMarkerLayer({
    //     name: 'clusterGroup',
    //     layer: new L.LayerGroup()
    // });
    // map.addMarkerLayer({
    //     name: 'powerlinesLayerGroup',
    //     layer: new L.LayerGroup()
    // });

    var _pgisMap = pgisMap;

    pgisMap.baseMapDataLoader = function() {
        MapDataLoader.loadBaseMapDataForMapFragment(
            pgisMap,
            this.markerLayers.markers,
            GalleryHelpers.getGalleryContainer(),
            GalleryHelpers.getGallery(),
            MapHelpers.getSplashScreen()
        );
    };

    pgisMap.baseMapDataLoader();

    window.pgisMap = pgisMap;
});
