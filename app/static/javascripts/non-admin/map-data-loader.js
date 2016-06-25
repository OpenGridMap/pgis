var MapDataLoader = {
  loadDataForMapFragment: function(pgisMap, markers, clusterGroup, powerlinesLayerGroup){
    var map = pgisMap.map;

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
            var marker = new L.Marker(data[i]['latlng']).on('click', onMarkerClick);
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
              icon: createClusterIcon(data[i])
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
  }

}
