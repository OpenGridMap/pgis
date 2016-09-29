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
    var selectedPointIcon = L.icon({
      iconUrl: 'static/images/marker-icon-red-2x.png',
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

          // don't delete a selected point from pgisMap.markerMap
          if (pgisMap.selectedPoint != null) {
            selectedPointReference = pgisMap.markerMap[pgisMap.selectedPoint];
            pgisMap.markerMap = {};
            pgisMap.markerMap[selectedPointReference.data.id] = selectedPointReference;
          } else {
            pgisMap.markerMap = {};
          }
          var newMarkers = [];
          for(var i = 0; i < data.length; i++){
            if(data[i]['revised'] == true) {
              var marker = new L.Marker(data[i]['latlng']).on('click', onMarkerClick);
            } else {
              var marker = new L.Marker(data[i]['latlng'], {icon: unverifiedIcon}).on('click', onMarkerClick);
            }
            marker.data = data[i];
            newMarkers.push(marker);
            pgisMap.markerMap[data[i].id] = marker;
          }
          markers.addLayers(newMarkers);
          if (pgisMap.selectedPoint != null) {
            pgisMap.markerMap[pgisMap.selectedPoint].setIcon(selectedPointIcon);
          }

          function onMarkerClick(e) {
            pgisMap.sidebar.setContent(
              MapHelpers.getPointSidebarContent(e.target.data)
            );
            if (!pgisMap.sidebar.isVisible()) {
              pgisMap.sidebar.show();
            }
            if (pgisMap.selectedPoint != null) {
              // deselect old point
              pgisMap.markerMap[pgisMap.selectedPoint].setIcon(new L.Icon.Default());
            }
            e.target.setIcon(selectedPointIcon);
            pgisMap.selectedPoint = e.target.data.id; // here a refernce to the point should be saved, not an id
          }
          map.fireEvent("dataload");

          // if user wants to jump to a specific point, open sidebar for this point
          if (pgisMap.point_id != null) {
            marker = pgisMap.markerMap[pgisMap.point_id];
            marker.setIcon(selectedPointIcon);
            pgisMap.selectedPoint = pgisMap.point_id;
            pgisMap.sidebar.setContent(MapHelpers.getPointSidebarContent(marker.data));
            pgisMap.sidebar.show();
            pgisMap.point_id = null;
          }
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
    var _this = this;

    ApiService.fetchRelationsData(pgisMap, function(data){
      relations = data;
      _this.plotRelationsOnMap(pgisMap, relations);
    });
  },

  plotRelationsOnMap: function(pgisMap, relations) {
    pgisMap.overlayLayers[pgisMap.selectedOverlayLayers[0]].layer.clearLayers();

    _.each(relations, function(relation){
      var relationFeatureLayer = L.pgisRelationFeatureGroup(relation);
      pgisMap.overlayLayers[pgisMap.selectedOverlayLayers[0]].layer.addLayer(relationFeatureLayer);

      // if relation with this id was previously selected for sidebar, hightlight it
      //  This is needed because when clicked on a relation, the display of sidebar
      //  moved the map triggering a reload of data and rerender of the layers
      if(typeof(pgisMap.overlayLayers[pgisMap.selectedOverlayLayers[0]].lastClickedRelationFeatureLayer) != 'undefined') {
        selectedRelationId = pgisMap.overlayLayers[pgisMap.selectedOverlayLayers[0]]
          .lastClickedRelationFeatureLayer.relation.id;

        if(relation.id == selectedRelationId) {
          // to highlight the relation as if its clicked for opening sidebar
          pgisMap.map.fireEvent("relation-click", {
            relationFeatureLayer: relationFeatureLayer
          });
        }
      }

      // if the relation was selected to be exported. Add the required highlighting
      selectedRelationsIds = (JSON.parse(localStorage.getItem('selectedRelations')) || [])
      if(selectedRelationsIds.indexOf(relation.id.toString()) > -1) {
        relationFeatureLayer.highlightForExport();
      }

      relationFeatureLayer.on('click', function(e) {
        // remove any relation layer that is already highlighted for sidebar
        if(typeof(pgisMap.overlayLayers[pgisMap.selectedOverlayLayers[0]].lastClickedRelationFeatureLayer) != 'undefined') {
          pgisMap.overlayLayers[pgisMap.selectedOverlayLayers[0]].lastClickedRelationFeatureLayer.removeHighlightForSidebar();
        }
        pgisMap.map.fireEvent("relation-click", { relationFeatureLayer: relationFeatureLayer });
      });
    });
  }
}