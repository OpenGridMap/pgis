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