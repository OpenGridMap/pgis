$(document).ready(function(){
	L.Icon.Default.imagePath = APP_IMAGES_URL;
	var map = L.map('map').setView([48.1333, 11.5667], 13);
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	}).addTo(map);
	L.Control.geocoder().addTo(map);

	var markers = new L.MarkerClusterGroup();
	map.addLayer(markers);
	var clusterGroup = new L.LayerGroup();
	map.addLayer(clusterGroup);
	var powerlines = new L.LayerGroup();
	map.addLayer(powerlines);
	loadMapFragment();

    var moveEndTimeout;
    
    map.on('moveend', function(){
        window.clearTimeout(moveEndTimeout);
        moveEndTimeout = window.setTimeout(function() {
            loadMapFragment();
        }, 500);
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
                        bindClickEvent(marker, data[i]);
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
                    powerlines.addLayer(L.polyline(data[i], {color: 'red'}));
                }
            }
        });
    }

    Handlebars.registerHelper('json', function(context) {
        return JSON.stringify(context, null, 4);
    });

    var source   = $("#marker-popup-template").html();
    var markerPopupTemplate = Handlebars.compile(source)
        
    function bindClickEvent(marker, point){
       var popup = L.popup()
                    .setContent(markerPopupTemplate(point))
       marker.bindPopup(popup);
    }

});
