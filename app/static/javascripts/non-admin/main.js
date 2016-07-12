$(document).ready(function(){
  registerHandleBarHelpers();

  var osmTile = MapHelpers.getOsmTile();
  var satelliteTile = MapHelpers.getSatelliteTile();

  var pgisMap = new PgisMap();
  pgisMap.createMap(osmTile);

  var map = pgisMap.map;

  var baseMaps = {
    "Satellite View": satelliteTile,
    "Topological View": osmTile
  };

  pgisMap.addBaseMaps(baseMaps);

  var newPointLinkProperties = {
    ref: 'newPoint',
    text: 'New Point',  // string
    onclick: function() {
      window.location.href = '/admin/points/new?redirect_back=true'
        + '&lat=' + pgisMap.map.getBounds().getCenter().lat
        + '&long=' + pgisMap.map.getBounds().getCenter().lng
        + '&zoom=' + pgisMap.map.getZoom();
    }
  };

  pgisMap.addLinkButton(newPointLinkProperties);

  var rankingTableLinkProperties = {
    ref: 'ranking',
    text: 'Top 10 Ranking',
    onclick: function() {
      window.location.href = '/ranking';
    }
  };

  pgisMap.addLinkButton(rankingTableLinkProperties);

  var userProfileLinkProperties = {
    ref: 'userprofile',
    text: 'Your Profile',
    onclick: function() {
      window.location.href = '/userprofile';
    }
  };

  pgisMap.addLinkButton(userProfileLinkProperties);

  pgisMap.addMarkerLayer({
    name: 'markers',
    layer: new L.MarkerClusterGroup()
  });

  pgisMap.addMarkerLayer({
    name: 'clusterGroup',
    layer: new L.LayerGroup()
  });

  pgisMap.addMarkerLayer({
    name: 'powerlinesLayerGroup',
    layer: new L.LayerGroup()
  });

  var _pgisMap = pgisMap;

  pgisMap.baseMapDataLoader = function() {
    if (_.contains(_pgisMap.selectedOverlayLayers, "Relations")) {
      MapDataLoader.fetchAndPlotRelations(_pgisMap);
    } else {
      MapDataLoader.loadBaseMapDataForMapFragment(
        this,
        this.markerLayers.markers,
        this.markerLayers.clusterGroup,
        this.markerLayers.powerlinesLayerGroup
      );
    }
  }

  pgisMap.baseMapDataLoader();

  pgisMap.addOverlayLayer({
    name: "Relations",
    ref: 'relations',
    layer: new L.LayerGroup()
  });

  window.pgisMap = pgisMap;

  pgisMap.onOverlayAdd  = function(layer) {
    _.each(_pgisMap.markerLayers, function(layer){
      layer.clearLayers();
    });

    this.baseMapDataLoader();
  };

  pgisMap.onOverlayRemove  = function(layer) {
    _.each(_pgisMap.markerLayers, function(layer){
      layer.clearLayers();
    });

    this.baseMapDataLoader();
  };
});
