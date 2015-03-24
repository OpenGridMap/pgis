$(document).ready(function(){
	L.Icon.Default.imagePath = APP_IMAGES_URL;
	var map = L.map('map').setView([48.1333, 11.5667], 13);
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	}).addTo(map);

	map.on('moveend', function(e){
		if(map.getZoom() > 7) {
			loadMapFragment()
		}
	})

	$.ajax({
		url : "/powerlines",
		success : function(data){
			for(var i = 0; i < data.length; i++){
				console.log(data[i])
				var polyline = L.polyline(data[i], {color: 'red'}).addTo(map);
			}
		}
	});

	loadMapFragment();

	function loadMapFragment(){
		$.ajax({
			url : "/points?bounds=" + latLngBoundsToStr(map.getBounds()),
			success : function(data){
				for(var i = 0; i < data.length; i++){
					var marker = L.marker(data[i]).addTo(map);
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
