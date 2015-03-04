$(document).ready(function(){
	L.Icon.Default.imagePath = APP_IMAGES_URL;


	var map = L.map('map').setView([48.1333, 11.5667], 13);

	var powerline = $(map.getContainer()).data('powerline');

	if(powerline != ""){
		var points_coords = powerline.split(",");
		var coords = [];
		for(var i = 0; i < points_coords.length; i++){
			var parts = points_coords[i].split(" ");
			coords[i] = []
			for(var j = 0; j < parts.length; j++){
				if(parts[j] != ""){
					coords[i].push(parseFloat(parts[j]));
				}
			}			
		}
		console.log(coords)
		var polyline = L.polyline(coords, {color: 'red'}).addTo(map);
	}

	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	}).addTo(map);
})