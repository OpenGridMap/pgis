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
		maxZoom: 18, minZoom: 8
	});

  var satellite_map = L.tileLayer('http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18, minZoom: 8
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
  L.control.layers(baseMaps).addTo(map);

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
    // adding sidebar
    var sidebar = L.control.sidebar('sidebar', {
        position: 'left'
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
    var unverifiedIcon = L.icon({
        iconUrl: 'static/images/marker-unverified-icon-2x.png',
        shadowUrl: 'static/images/marker-shadow.png',
        iconSize:    [25, 41],
		iconAnchor:  [12, 41],
		popupAnchor: [1, -34],
		shadowSize:  [41, 41]
    });
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
                    var newMarkers = [];
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
    }
    

    function clusterClickEvent(){
        

    }

});
