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

	function loadMapFragment(){
        if(map.getZoom() > 12) {
            $.ajax({
                url : "/points",
                data: {
                    "bounds" : map.getBounds().toBBoxString() 
                },
                success : function(data){
                    markers.clearLayers();
                    for(var i = 0; i < data.length; i++){
                        var marker = new L.Marker(data[i]['latlng']);
                        var popupContent = "<b>Name:</b> " + data[i]['name'];
                        popupContent += "<br />";
                        popupContent += "<b>Latitude:</b> " + data[i]['latlng'][0];
                        popupContent += "<br />";
                        popupContent += "<b>Longitude:</b> " + data[i]['latlng'][1];

                        marker.bindPopup(popupContent)
                        markers.addLayer(marker);
                    }			
                }
            });
        }
    }

    map.on('moveend', function(){
        loadMapFragment();
    })

});
