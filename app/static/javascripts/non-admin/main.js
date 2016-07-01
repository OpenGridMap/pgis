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

  // var newPointLink = L.control.link_button(newPointLinkProperties).addTo(map);
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
      console.log("Not loading base data because relations are selected");
    } else {
      MapDataLoader.loadDataForMapFragment(
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
    // TODO: Do this only if it is a Relations layr
    // if (target.name == 'Relations') {
    //
    _.each(_pgisMap.markerLayers, function(layer){
      layer.clearLayers();
    });

    var defaultStyle = {
      color: "red"
    }
    var highlightedStyle = {
      color: "blue"
    }

    ApiService.fetchRelationsData(_pgisMap, function(data){

      relations = data;

      _.each(relations, function(relation){
        var relationFeatureLayer = L.featureGroup();

        _.each(relation.powerlines, function(line){
          var polyline = L.polyline(line.latlngs);
          polyline.setStyle(defaultStyle);

          relationFeatureLayer.addLayer(polyline);
        });

        var markersLayer =  new L.PgisMarkerClusterGroup();

        var markers = []
        _.each(relation.points, function(point){
          var marker = new L.Marker(point.latlng)
          marker.setIcon(markersLayer.getMarkerDefaultIcon())
          markers.push(marker);
        });
        markersLayer.addLayers(markers);
        relationFeatureLayer.addLayer(markersLayer);

        markersLayer.on("clustermouseover", function(e){
          markersLayer.addHighlightStyle();
        })

        markersLayer.on("clustermouseout", function(e){
          markersLayer.removeHighlightStyle();
        })

        relationFeatureLayer.on("mouseover", function(e){
          markersLayer.addHighlightStyle();
          e.target.setStyle(highlightedStyle);
        });

        relationFeatureLayer.on("mouseout", function(e){
          markersLayer.removeHighlightStyle();
          e.target.setStyle(defaultStyle);
        });

        pgisMap.overlayLayers.relations.layer.addLayer(relationFeatureLayer);
      });
    });
  };
});
