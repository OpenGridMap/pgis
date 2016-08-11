// Will make more sense to rename this as MapDataHandler.
//  It fetches the data and plots it on the map.

var MapDataLoader = {
  loadBaseMapDataForMapFragment: function(pgisMap, markers, clusterGroup, powerlinesLayerGroup){
    var map = pgisMap.map;
    var unverifiedIcon = L.icon({
      iconUrl: 'static/images/marker-unverified-icon-2x.png',
      shadowUrl: 'static/images/marker-shadow.png',
      iconSize:    [25, 41],
      iconAnchor:  [12, 41],
      popupAnchor: [1, -34],
      shadowSize:  [41, 41]
    });

    if(map.getZoom() > 11) {
      map.fireEvent("dataloading");
      $.ajax({
        url : "/points",
        data: {
          "bounds" : map.getBounds().toBBoxString()
        },
        success : function(data){
          // Clear both layers that plot points!
          markers.clearLayers();
          clusterGroup.clearLayers();

          var newMarkers = []
          markerMap = {};
          for(var i = 0; i < data.length; i++){
            if(data[i]['revised'] == true) {
              var marker = new L.Marker(data[i]['latlng']).on('click', onMarkerClick);
            } else {
              var marker = new L.Marker(data[i]['latlng'], {icon: unverifiedIcon}).on('click', onMarkerClick);
            }
            marker.data = data[i];
            newMarkers.push(marker);
            markerMap[data[i].id] = marker;
          }
          markers.addLayers(newMarkers);

          function onMarkerClick(e) {
            pgisMap.sidebar.setContent(MapHelpers.getPointSidebarContent(e.target.data));
            if (!pgisMap.sidebar.isVisible()) {
              pgisMap.sidebar.show()
            }
          }
          map.fireEvent("dataload");
        }
      });
    } else {
      map.fireEvent("dataloading");
      $.ajax({
        url : "/points/clustered",
        data : {
          "zoom" : map.getZoom(),
          "bounds" : map.getBounds().toBBoxString()
        },
        success : function(data){
          // Clear both layers that plot points!
          markers.clearLayers();
          clusterGroup.clearLayers();

          for(var i = 0; i < data.length; i++){
            var marker = new L.Marker(data[i]['latlng'], {
              icon: MiscHelpers.createClusterIcon(data[i])
            });
            marker.panelOpen = false;
            clusterGroup.addLayer(marker);
            marker.on('click', function(e){
              map.setView(e.target.getLatLng(), map.getZoom() + 1);
            });
          }
          map.fireEvent("dataload");
        }
      });
    }

    map.fireEvent("dataloading");

    $.ajax({
      url : "/powerlines",
      data : {
        "bounds"    : map.getBounds().toBBoxString(),
        "zoom"      : map.getZoom()
      },
      success : function(data){
        powerlinesLayerGroup.clearLayers();
        for(var i = 0; i < data.length; i++){
          var polyline = L.polyline(data[i].latlngs, {color: 'red'});
          MapHelpers.bindPowerlinePopup(polyline, data[i]);
          powerlinesLayerGroup.addLayer(polyline);
        }
        map.fireEvent("dataload");
      }
    });
  },

  fetchAndPlotRelations: function(pgisMap) {
    ApiService.fetchRelationsData(pgisMap, function(data){

      relations = data;

      pgisMap.overlayLayers.relations.layer.clearLayers();

      _.each(relations, function(relation){
        var relationFeatureLayer = L.pgisRelationFeatureGroup(relation);
        pgisMap.overlayLayers.relations.layer.addLayer(relationFeatureLayer);

        relationFeatureLayer.on('click', function(e) {
          pgisMap.overlayLayers.relations
            .lastClickedRelationFeatureLayer = this;

          MapHelpers.setSidebarContentToLastClickedRelation(
            pgisMap,
            (JSON.parse(localStorage.getItem('selectedRelations')) || [])
          );

          if (!pgisMap.sidebar.isVisible()) {
            pgisMap.sidebar.show();
          }
        });
      });
    });
  }
}
