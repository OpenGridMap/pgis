var getQueryString = function ( field, url ) {
  var href = url ? url : window.location.href;
  var reg = new RegExp( '[?&]' + field + '=([^&#]*)', 'i' );
  var string = reg.exec(href);
  return string ? string[1] : null;
};

$(document).ready(function(){
  L.Icon.Default.imagePath = APP_IMAGES_URL;


  var lat = getQueryString("lat");
  var lng = getQueryString("long");
  var center = [48.1333, 11.5667];
  if(lat && lng){
    center = [lat, lng];
  }


  var zoom = getQueryString("zoom") || 13;

  var osm_map = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    minZoom: 8
  });

  var satellite_map = L.tileLayer('http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    minZoom: 8
  });
  var map = L.map('map', {
    layers: [osm_map]
  }).setView(center, zoom);
  if (!lat && !lng) {
    map.locate({setView : true});
  }

  var loadingControl = L.Control.loading({
    separate: true
  });
  map.addControl(loadingControl);

  var bounds = getQueryString("bounds");

  if( bounds) {
    bounds = bounds.split("%2C");
    console.log(bounds);
    map.fitBounds([
      [bounds[0], bounds[1]],
      [bounds[2], bounds[3]]
    ]);
  }

  var baseMaps = {
    "Satellite View": satellite_map,
    "Topological View": osm_map
  };
  L.Control.geocoder().addTo(map);
  var layerControl = L.control.layers(baseMaps).addTo(map);

  var newPointLinkProperties = {
    'text': 'New Point',  // string
    'onclick': function() { window.location.href = '/admin/points/new?redirect_back=true&lat=' + map.getBounds().getCenter().lat + '&long=' + map.getBounds().getCenter().lng + '&zoom=' + map.getZoom(); }
  };

  var newPointLink = L.control.link_button(newPointLinkProperties).addTo(map);


  var markers = new L.MarkerClusterGroup();
  map.addLayer(markers);

  var clusterGroup = new L.LayerGroup();
  map.addLayer(clusterGroup);

  var powerlines = new L.LayerGroup();
  map.addLayer(powerlines);

  var relationsLayer = new L.LayerGroup();
  // map.addLayer(relationsLayer)
  layerControl.addOverlay(relationsLayer, "Relations")

  // adding sidebar
  var sidebar = L.control.sidebar('sidebar', {
    position: 'right'
  });
  map.addControl(sidebar);

  loadMapFragment();
  var loadFragmentDebounced = _.debounce(loadMapFragment, 1000);
  map.on('moveend', function(){
    loadFragmentDebounced();
  });

  var markerMap = {};

  //Adapted from https://github.com/Leaflet/Leaflet.markercluster/issues/217#issuecomment-20963103
  var iconCreateFunction = function (cluster) {

    var count = cluster.count;

    // cluster icon
    var c = 'marker-cluster-';
    if (count < 10) {
      c += 'small';
    } else if (count < 100) {
      c += 'medium';
    } else {
      c += 'large';
    }

    return new L.DivIcon({
      html: '<div><span>' + count + '</span></div>',
      className: 'marker-cluster ' + c,
      iconSize: new L.Point(40, 40)
    });
  };

  function loadMapFragment(){
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
            sidebar.setContent(getPointSidebarContent(e.target.data));
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
              icon: iconCreateFunction(data[i])
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
        powerlines.clearLayers();
        for(var i = 0; i < data.length; i++){
          var polyline = L.polyline(data[i].latlngs, {color: 'red'});
          bindPowerlinePopup(polyline, data[i]);
          powerlines.addLayer(polyline);
        }
        map.fireEvent("dataload");
      }
    });
  }

  Handlebars.registerHelper('json', function(context) {
    return JSON.stringify(context, null, 4);
  });

  var source   = $("#marker-sidebar-template").html();
  var markerSidebarTemplate = Handlebars.compile(source);

  var source   = $("#polyline-popup-template").html();
  var polylinePopupTemplate = Handlebars.compile(source);

  /* function bindMarkerPopup(marker, point){
     var popup = L.popup()
     .setContent(markerPopupTemplate(point));
     marker.bindPopup(popup);
     } */

  function getPointSidebarContent(pointdata){
    return markerSidebarTemplate(pointdata);
  }

  function bindPowerlinePopup(polyline, powerline){
    var popup = L.popup()
                  .setContent(polylinePopupTemplate(powerline));
    polyline.bindPopup(popup);
    polyline.on("click", function(e){
      console.log(e);
      console.log(powerline);
      console.log(JSON.stringify(powerline));
    })
  }


  var linesJSON = '{"relations":[{"lines":[{"id":6845,"latlngs":[[48.1527458,11.4455838],[48.1527967,11.4461609],[48.1525911,11.4478677],[48.1524774,11.4489395],[48.1523372,11.4499599],[48.1519867,11.45102],[48.1517063,11.4519937],[48.1517245,11.4522968]],"tags":{"cables":"4","power":"minor_line"}},{"id":6844,"latlngs":[[48.1527933,11.4456013],[48.1529378,11.4460683],[48.1528552,11.446854],[48.1527856,11.4477353],[48.1527218,11.4486112],[48.1526651,11.4493173],[48.1526191,11.4499455],[48.1523133,11.4506215],[48.1520559,11.4511754],[48.1517245,11.4522968],[48.1517516,11.4530459],[48.1517319,11.4538116],[48.1515753,11.4551884],[48.1514424,11.4558429],[48.1510736,11.4572801],[48.1508579,11.4580301],[48.1502883,11.4594815],[48.1500713,11.4600873]],"tags":{"cables":"4","power":"minor_line"}},{"id":87,"latlngs":[[48.1783778,11.4152557],[48.1763266,11.416423],[48.1745902,11.4173557],[48.1730978,11.4182201],[48.170821,11.4178794],[48.169401,11.4205243],[48.1675677,11.4239089],[48.165768,11.427166],[48.1640308,11.430358],[48.1626126,11.4329517],[48.1614383,11.4350706],[48.1598162,11.4380796],[48.1581959,11.4406373],[48.1565812,11.4432294],[48.154749,11.4436157],[48.1531975,11.4440889]],"tags":{"cables":"8","fixme":"Nachdem Ltg. Pasing-Augsburg durch Karlsfeld-Augsburg ersetzt ist, ist zu klären, wie die 4 Seile Pasing-Augsburg jetzt verwendet werden. Demontiert?","frequency":"16.7","name":"Karlsfeld - Pasing","operator":"DB_Energie","power":"line","voltage":"110000","wires":"single"}}]},{"lines":[{"id":237,"latlngs":[[48.1366621,11.6505875],[48.1363067,11.6503092],[48.1357454,11.6499191],[48.1352488,11.6494987],[48.135044,11.6490031],[48.1348762,11.6485064],[48.134761,11.6480349],[48.1346907,11.6475585],[48.1346346,11.646996],[48.1346346,11.646531]],"tags":{"frequency":"16.7","operator":"DB_Energie","power":"minor_line","voltage":"15000"}},{"id":61,"latlngs":[[48.184663,11.6505435],[48.1836259,11.6502098],[48.1818437,11.6496165],[48.1794446,11.6505446],[48.1767833,11.6515747],[48.1744916,11.6524376],[48.1721119,11.6533528],[48.1696649,11.6542986],[48.1674989,11.6542392],[48.1653351,11.6541855],[48.1631336,11.654125],[48.1614898,11.6540818],[48.1591813,11.6540116],[48.1570752,11.6539697],[48.1546807,11.6538827],[48.1524123,11.6538195],[48.1501191,11.6537537],[48.1477784,11.6536884],[48.145505,11.6536265],[48.1433102,11.6535645],[48.1413471,11.6535032],[48.1390064,11.652896],[48.1375582,11.6506381]],"tags":{"cables":"4","frequency":"16.7","name":"Karlsfeld - München Ost;München Ost - Aufkirchen","operator":"DB_Energie","power":"line","voltage":"110000","wires":"single"}}]}]}'



  var relations = JSON.parse(linesJSON).relations;
  var defaultStyle = {
    color: "red"
  }
  var highlightedStyle = {
    color: "blue"
  }

  _.each(relations, function(relation){
    var lines = relation.lines
    var relationFeatureLayer = L.featureGroup();
    for(var i = 0; i < lines.length; i++){
      console.log("in powerline lopp")
      var polyline = L.polyline(lines[i].latlngs);
      polyline.setStyle(defaultStyle);
      // bindPowerlinePopup(polyline, lines[i]);
      relationFeatureLayer.addLayer(polyline);
    }
    relationFeatureLayer.on("mouseover", function(e){
      e.target.setStyle(highlightedStyle);
    });

    relationFeatureLayer.on("mouseout", function(e){
      e.target.setStyle(defaultStyle);
    })

    relationsLayer.addLayer(relationFeatureLayer);
  });
  window.relationsLayer = relationsLayer;


  map.selectArea.enable();

  map.on('areaselected', function(e){
    console.log(e.bounds);
    window.selectedBounds = e.bounds;
    relationsLayer.eachLayer(function(featureLayer){
      featureLayer.eachLayer(function(relationElementLayer){
        if(e.bounds.intersects(relationElementLayer.getLatLngs())){
          relationElementLayer.setStyle(highlightedStyle);
        }
      });
    });
  });

  map.addEventListener("overlayadd", function(target, layerName){
    // TODO: Do this only if it is a Relations layr
    _.each(target.layer.getLayers(), function(featureLayer){
      // this assumes that all the layers added to the relationsLayers
      // are all FeatureLayers. +bringToFront+ is available only on
      // FeatureLayers.
      // TODO: This again goes to back when zoom is changed.
      featureLayer.bringToFront();
    });
  });

  window.map = map;

  map.on("boxzoomend", function(e) {
    console.log("you just finished dragging")
    window.e = e;
    _.each(relations, function(relation){
      //
    })
    // for (var i = 0; i < markers.length; i++) {
    //   if (e.boxZoomBounds.contains(markers[i])) {
    //     console.log(markers[i]);
    //   }
    // }
  });

  function clusterClickEvent(){


  }

});
