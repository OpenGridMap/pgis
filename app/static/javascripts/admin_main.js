function latlngStringToCoords(powerline){
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

	return coords;
}

function polylineToString(polyline){
	return polyline.getLatLngs().map(function(latlng) { return [latlng.lat, latlng.lng].join(" ")  }).join(",")
}
L.Icon.Default.imagePath = APP_IMAGES_URL;


$('.textarea-json-beautify-button').on('click', function(){
	var textarea = $(this).closest('.form-group').find('.json-propeties-textarea')

	try {
		var json = JSON.parse(textarea.val());
		textarea.val(JSON.stringify(json, null, "\t"));
	} catch(e){
	}
});
