var getQueryString = function ( field, url ) {
    var href = url ? url : window.location.href;
    var reg = new RegExp( '[?&]' + field + '=([^&#]*)', 'i' );
    var string = reg.exec(href);
    return string ? string[1] : null;
};

L.Control.Button = L.Control.extend({
  options: {
    position: 'bottomleft'
  },
  initialize: function (options) {
    this._button = {};
    this.setButton(options);
  },

  onAdd: function (map) {
    this._map = map;
    var container = L.DomUtil.create('div', 'leaflet-control-button');
	
    this._container = container;
    
    this._update();
    return this._container;
  },

  onRemove: function (map) {
  },

  setButton: function (options) {
    var button = {
      'text': options.text,                 //string
      'iconUrl': options.iconUrl,           //string
      'onClick': options.onClick,           //callback function
      'hideText': !!options.hideText,         //forced bool
      'maxWidth': options.maxWidth || 70,     //number
      'doToggle': options.toggle,			//bool
      'toggleStatus': false					//bool
    };

    this._button = button;
    this._update();
  },
  
  getText: function () {
  	return this._button.text;
  },
  
  getIconUrl: function () {
  	return this._button.iconUrl;
  },
  
  destroy: function () {
  	this._button = {};
  	this._update();
  },
  
  toggle: function (e) {
  	if(typeof e === 'boolean'){
  		this._button.toggleStatus = e;
  	}
  	else{
  		this._button.toggleStatus = !this._button.toggleStatus;
  	}
  	this._update();
  },
  
  _update: function () {
    if (!this._map) {
      return;
    }

    this._container.innerHTML = '';
    this._makeButton(this._button);
 
  },

  _makeButton: function (button) {
    var newButton = L.DomUtil.create('div', 'leaflet-buttons-control-button', this._container);
    if(button.toggleStatus)
    	L.DomUtil.addClass(newButton,'leaflet-buttons-control-toggleon');
        
    var image = L.DomUtil.create('img', 'leaflet-buttons-control-img', newButton);
    image.setAttribute('src',button.iconUrl);
    
    if(button.text !== ''){

      L.DomUtil.create('br','',newButton);  //there must be a better way

      var span = L.DomUtil.create('span', 'leaflet-buttons-control-text', newButton);
      var text = document.createTextNode(button.text);  //is there an L.DomUtil for this?
      span.appendChild(text);
      if(button.hideText)
        L.DomUtil.addClass(span,'leaflet-buttons-control-text-hide');
    }

    L.DomEvent
      .addListener(newButton, 'click', L.DomEvent.stop)
      .addListener(newButton, 'click', button.onClick,this)
      .addListener(newButton, 'click', this._clicked,this);
    L.DomEvent.disableClickPropagation(newButton);
    return newButton;

  },
  
  _clicked: function () {  //'this' refers to button
  	if(this._button.doToggle){
  		if(this._button.toggleStatus) {	//currently true, remove class
  			L.DomUtil.removeClass(this._container.childNodes[0],'leaflet-buttons-control-toggleon');
  		}
  		else{
  			L.DomUtil.addClass(this._container.childNodes[0],'leaflet-buttons-control-toggleon');
  		}
  		this.toggle();
  	}
  	return;
  }

});

$(document).ready(function(){
	L.Icon.Default.imagePath = APP_IMAGES_URL;

  var lat = getQueryString("lat");
  var lng = getQueryString("long");
  var center = [48.1333, 11.5667];
  if(lat && lng){
    center = [lat, lng];
  }

  var zoom = getQueryString("zoom") || 13;

  var osm_map = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	});

  var satellite_map = L.tileLayer('http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
		maxZoom: 18
	});
  var map = L.map('map', {
    layers: [osm_map] 
  }).setView(center, zoom);

  var baseMaps = {
    "Satellite View": satellite_map,
    "Topological View": osm_map
  };
	L.Control.geocoder().addTo(map);
  L.control.layers(baseMaps).addTo(map);

  var myButtonOptions = {
    'text': 'MyButton',  // string
    'iconUrl': 'images/myButton.png',  // string
    'onClick': my_button_onClick,  // callback function
    'hideText': true,  // bool
    'maxWidth': 30,  // number
    'doToggle': false,  // bool
    'toggleStatus': false  // bool
  }   

  var myButton = new L.Control.Button(myButtonOptions).addTo(map);
  function my_button_onClick() {
    console.log("someone clicked my button");
  }

	var markers = new L.MarkerClusterGroup();
	map.addLayer(markers);
	var clusterGroup = new L.LayerGroup();
	map.addLayer(clusterGroup);
	var powerlines = new L.LayerGroup();
	map.addLayer(powerlines);
	loadMapFragment();

    var loadFragmentDebounced = _.debounce(loadMapFragment, 1000);
    map.on('moveend', function(){
      loadFragmentDebounced();
    });

    var markerMap = {};
    
    //Adapted from https://github.com/Leaflet/Leaflet.markercluster/issues/217#issuecomment-20963103
    var iconCreateFunction = function (cluster) {

        var count = cluster.count;

        // cluster icon
        var c = 'marker-cluster-';
        if (count < 10) {
            c += 'small';
        } else if (count < 100) {
            c += 'medium';
        } else {
            c += 'large';
        }

        return new L.DivIcon({
            html: '<div><span>' + count + '</span></div>',
            className: 'marker-cluster ' + c,
            iconSize: new L.Point(40, 40)
        });
    };

	function loadMapFragment(){
        if(map.getZoom() > 11) {
            $.ajax({
                url : "/points",
                data: {
                    "bounds" : map.getBounds().toBBoxString() 
                },
                success : function(data){
                    markers.clearLayers();
                    clusterGroup.clearLayers();
                    var newMarkers = []
                    markerMap = {};
                    for(var i = 0; i < data.length; i++){
                        var marker = new L.Marker(data[i]['latlng']);
                        marker.panelOpen = false;
                        bindMarkerPopup(marker, data[i]);
                        newMarkers.push(marker);
                        markerMap[data[i].id] = marker;
                    }			
                    markers.addLayers(newMarkers);
                }
            });
        } else {
            $.ajax({
                url : "/points/clustered",
                data : {
                    "zoom" : map.getZoom(),
                    "bounds" : map.getBounds().toBBoxString() 
                },
                success : function(data){
                    markers.clearLayers();
                    clusterGroup.clearLayers();
                    for(var i = 0; i < data.length; i++){
                        var marker = new L.Marker(data[i]['latlng'], {
                            icon: iconCreateFunction(data[i])
                        });
                        marker.panelOpen = false;
                        clusterGroup.addLayer(marker);
                        marker.on('click', function(e){
                            map.setView(e.target.getLatLng(), map.getZoom() + 1);
                        });
                    }			
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
                powerlines.clearLayers();
                for(var i = 0; i < data.length; i++){
                    var polyline = L.polyline(data[i].latlngs, {color: 'red'});
                    bindPowerlinePopup(polyline, data[i]);
                    powerlines.addLayer(polyline);
                }
            }
        });
    }

    Handlebars.registerHelper('json', function(context) {
        return JSON.stringify(context, null, 4);
    });

    var source   = $("#marker-popup-template").html();
    var markerPopupTemplate = Handlebars.compile(source);
        
    var source   = $("#polyline-popup-template").html();
    var polylinePopupTemplate = Handlebars.compile(source);

    function bindMarkerPopup(marker, point){
       var popup = L.popup()
                    .setContent(markerPopupTemplate(point));
       marker.bindPopup(popup);
    }

    function bindPowerlinePopup(polyline, powerline){
       var popup = L.popup()
                    .setContent(polylinePopupTemplate(powerline));
       polyline.bindPopup(popup);
    }
    

    function clusterClickEvent(){
        
    }

});
