$(document).ready(function(){
	L.Icon.Default.imagePath = APP_IMAGES_URL;
	var map = L.map('map').setView([48.1333, 11.5667], 13);
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	}).addTo(map);
	
	var markers = new L.MarkerClusterGroup();
	loadMapFragment();
	map.addLayer(markers);

	$.ajax({
		url : "/powerlines",
		success : function(data){
			for(var i = 0; i < data.length; i++){
				var polyline = L.polyline(data[i], {color: 'red'}).addTo(map);
			}
		}
	});

    map.on('moveend', function(){
        loadMapFragment();
    });

	function loadMapFragment(){
        if(map.getZoom() > 11) {
            $.ajax({
                url : "/points",
                data: {
                    "bounds" : map.getBounds().toBBoxString() 
                },
                success : function(data){
                    markers.clearLayers();
                    var newMarkers = []
                    for(var i = 0; i < data.length; i++){
                        var marker = new L.Marker(data[i]['latlng']);
                        marker.bindPopup(markerPopupContent(data[i]))
                        newMarkers.push(marker);
                    }			
                    markers.addLayers(newMarkers);
                }
            });
        }
    }

    function markerPopupContent(point){
        var popupContent = "<b>Name:</b> " + point['name'];
        popupContent += "<br />";
        popupContent += "<b>Latitude:</b> " + point['latlng'][0];
        popupContent += "<br />";
        popupContent += "<b>Longitude:</b> " + point['latlng'][1];
        return popupContent;
    }


});
