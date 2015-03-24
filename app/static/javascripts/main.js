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
		$.ajax({
			url : "/points",
			success : function(data){
				for(var i = 0; i < data.length; i++){
					markers.addLayer(new L.Marker(data[i]));
				}			
			}
		});
	}

})


function latLngBoundsToStr(latLngBounds) {
	bounds = "";
	bounds += latLngBounds.getSouth() + ","; 
	bounds += latLngBounds.getWest() + ",";
	bounds += latLngBounds.getNorth() + ",";
	bounds += latLngBounds.getEast();   
	return bounds;
}
