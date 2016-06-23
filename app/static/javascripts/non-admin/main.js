

function basicDraw() {

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

  var loadFragmentDebounced = _.debounce(loadDataForMapFragment, 1000);
  loadFragmentDebounced(
    pgisMap.map,
    pgisMap.markerLayers.markers,
    pgisMap.markerLayers.clusterGroup,
    pgisMap.markerLayers.powerlinesLayerGroup
  );

  map.on('moveend', function(){
    loadFragmentDebounced(
      pgisMap.map,
      pgisMap.markerLayers.markers,
      pgisMap.markerLayers.clusterGroup,
      pgisMap.markerLayers.powerlinesLayerGroup
    );
  });

  var markerMap = {};

}

function loadDataForMapFragment(map, markers, clusterGroup, powerlinesLayerGroup){
  if(map.getZoom() > 11) {
    map.fireEvent("dataloading");
    $.ajax({
      url : "/points",
      data: {
        "bounds" : map.getBounds().toBBoxString()
      },
      success : function(data){
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
          sidebar.setContent(MapHelpers.getPointSidebarContent(e.target.data));
          if (!sidebar.isVisible()) {
            sidebar.show()
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

$(document).ready(function(){
  registerHandleBarHelpers();
  basicDraw();
});
