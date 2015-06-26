$(document).ready(function(){
	L.Icon.Default.imagePath = APP_IMAGES_URL;
	var map = L.map('map').setView([48.1333, 11.5667], 13);
	L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	}).addTo(map);
	
	var markers = new L.MarkerClusterGroup();
	map.addLayer(markers);
	var powerlines = new L.LayerGroup();
	map.addLayer(powerlines);
	loadMapFragment();
    
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

    var markerMap = {};

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
        }

        $.ajax({
            url : "/powerlines",
            data : {
                "bounds"    : map.getBounds().toBBoxString(),
                "zoom"      : map.getZoom() 
            },
            success : function(data){
                for(var i = 0; i < 1000; i++){
                    powerlines.addLayer(L.polyline(data[i], {color: 'red'}));
                }
            }
        });
    }

    Handlebars.registerHelper('json', function(context) {
        return JSON.stringify(context, null, 4);
    });

    var mapControlPanel = $('#map-control-panel');
    var source   = $("#map-control-panel-content").html();
    var mapControlPanelContentTemplate = Handlebars.compile(source)
        
    map.on('resize', function () {
        $('#map').css("height", $(window).height() - mapControlPanel.height()  );
    });

    function bindClickEvent(marker, point){
        marker.on('click', function(){
            mapControlPanel.html(mapControlPanelContentTemplate(point));
            mapControlPanel.slideDown(function(){
                map.invalidateSize();
            });
        });
    }

    mapControlPanel.on('click', '.close-panel', function(){
        mapControlPanel.slideUp(function(){
            $('#map').css("height", $(window).height());
        });
    });

    var editToolbar = new L.EditToolbar.Edit(map, {
        featureGroup: drawnItems,
        selectedPathOptions: drawControl.options.edit.selectedPathOptions
    });

    mapControlPanel.on('click', '.edit-map-entity', function(e){
    });

});
