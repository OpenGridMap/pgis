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
    
    // Initialise the FeatureGroup to store editable layers
    var drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Initialise the draw control and pass it the FeatureGroup of editable layers
    var drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: false,
            circle: false,
            rectangle: false,
        },
    });
    map.addControl(drawControl);

    map.on('draw:created', function (e) {
        drawnItems.clearLayers(); // allow only one element drawn
        var type = e.layerType,
        layer = e.layer;
        drawnItems.addLayer(layer);
        markers.eachLayer(function(marker){
            marker.setOpacity(0.5);
        });
    }); 
    
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
                        bindClickEvent(marker, data[i]);
                        newMarkers.push(marker);
                    }			
                    markers.addLayers(newMarkers);
                    if(drawnItems.getLayers().length > 0){
                        markers.eachLayer(function(marker){
                            marker.setOpacity(0.5);
                        });
                    }
                }
            });
        }
    }

    Handlebars.registerHelper('json', function(context) {
        return JSON.stringify(context, null, '\t');
    });

    var markerModal = $('#markerModal');
    var source   = $("#marker-modal-content-template").html();
    var markerModalContentTemplate = Handlebars.compile(source)

    function bindClickEvent(marker, point){
        marker.on('click', function(){
            var content = markerModalContentTemplate(point);
            console.log(point)
            markerModal.find('.modal-content').html(content);
            markerModal.modal("show");
        });
    }

});
