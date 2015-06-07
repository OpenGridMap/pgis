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
            featureGroup: drawnItems,
            remove: false,
            edit: false
        },
        draw: false
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
        return JSON.stringify(context, null, 4);
    });

    var mapControlPanel = $('#map-control-panel');
    var source   = $("#map-control-panel-content").html();
    var mapControlPanelContentTemplate = Handlebars.compile(source)

    function bindClickEvent(marker, point){
        marker.on('click', function(){
           mapControlPanel.html(mapControlPanelContentTemplate(point));
           mapControlPanel.slideDown();
        });
    }

    mapControlPanel.on('click', '.close-panel', function(){
        mapControlPanel.slideUp();
    });

    mapControlPanel.on('click', '.edit-map-entity', function(e){
        // Disable drag and zoom handlers.
        map.dragging.disable();
        map.touchZoom.disable();
        map.doubleClickZoom.disable();
        map.scrollWheelZoom.disable();

        mapControlPanel.find('.save-map-entity').show();
        mapControlPanel.find('.cancel-map-entity-edit').show();
        $(e.target).hide();

        var id = $(this).data('id')
        var marker = markerMap[id];
        markers.removeLayer(marker);
        drawnItems.addLayer(marker);
        $(marker._icon).addClass('leaflet-edit-marker-selected leaflet-marker-draggable');

        var edit = new L.EditToolbar.Edit(map, {
                featureGroup: drawnItems,
                selectedPathOptions: drawControl.options.edit.selectedPathOptions
        }).enable();
        
    });
});
