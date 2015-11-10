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
		maxZoom: 18, minZoom: 9
	});

  var satellite_map = L.tileLayer('http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18, minZoom: 9
	});
  var map = L.map('map', {
    layers: [osm_map] 
  }).setView(center, zoom);

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
  L.control.layers(baseMaps).addTo(map);

  var newPointLinkProperties = {
    'text': 'New Point',  // string
    'href': '/admin/points/new?redirect_back=true'
  }   

  var newPointLink = L.control.link_button(newPointLinkProperties).addTo(map);

  var newPowerlineLinkProperties = {
    'text': 'New Powerline',  // string
    'href': '/admin/powerlines/new?redirect_back=true'
  }   
  var newPowerlineLink = L.control.link_button(newPowerlineLinkProperties).addTo(map);

	var markers = new L.MarkerClusterGroup();
	map.addLayer(markers);
	var clusterGroup = new L.LayerGroup();
	map.addLayer(clusterGroup);
	var powerlines = new L.LayerGroup();
	map.addLayer(powerlines);
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
                        var marker = new L.Marker(data[i]['latlng']);
                        marker.panelOpen = false;
                        bindMarkerPopup(marker, data[i]);
                        newMarkers.push(marker);
                        markerMap[data[i].id] = marker;
                    }			
                    markers.addLayers(newMarkers);
                }
            });
        } else {
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
                }
            });
        }

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
            }
        });
    }

    Handlebars.registerHelper('json', function(context) {
        return JSON.stringify(context, null, 4);
    });

    var source   = $("#marker-popup-template").html();
    var markerPopupTemplate = Handlebars.compile(source);
        
    var source   = $("#polyline-popup-template").html();
    var polylinePopupTemplate = Handlebars.compile(source);

    function bindMarkerPopup(marker, point){
       var popup = L.popup()
                    .setContent(markerPopupTemplate(point));
       marker.bindPopup(popup);
    }

    function bindPowerlinePopup(polyline, powerline){
       var popup = L.popup()
                    .setContent(polylinePopupTemplate(powerline));
       polyline.bindPopup(popup);
    }
    

    function clusterClickEvent(){
        

    }

});
