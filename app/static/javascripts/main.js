//alert('test')


$(document).ready(function(){
	L.Icon.Default.imagePath = APP_IMAGES_URL;
	var map = L.map('map').setView([48.1333, 11.5667], 13);
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	}).addTo(map);

	var latlngs = [[48.1533, 11.5667], [48.1423, 11.5697]]
	var polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);


	$.ajax({
		url : "/points",
		success : function(data){
			for(var i = 0; i < data.length; i++){
				var marker = L.marker(data[i], {draggable:'true'}).addTo(map);
			}			
		}
	});
})