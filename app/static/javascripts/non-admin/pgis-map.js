function PgisMap() {

  this.lat               = MiscHelpers.getQueryString("lat");
  this.lng               = MiscHelpers.getQueryString("long");
  this.boundsQueryString = MiscHelpers.getQueryString("bounds");
  this.zoom              = MiscHelpers.getQueryString("zoom") || 13;
  this.bounds            = undefined;
  this.center            = undefined;
  this.map               = undefined; // Leadlet's map object
  this.baseLayersControl = undefined;
  this.baseLayer         = undefined;
  this.linkButtons       = {}
  // Add any kind of marker layers to this.markerLayers
  //   e.g: L.MarkerClusterGroup(), L.LayerGroup() etc.
  this.markerLayers      = {};

  this.createMap = function(baseLayer) {
    L.Icon.Default.imagePath = APP_IMAGES_URL;
    this.baseLayer = baseLayer;

    if(this.lat && this.lng){
      this.center = [this.lat, this.lng];
    } else {
      this.center = [48.1333, 11.5667];
    }

    this.map = L.map('map', {
      layers: [this.baseLayer]
    }).setView(this.center, this.zoom);

    if (!this.lat && !this.lng) {
      this.map.locate({setView : true});
    }

    if (this.boundsQueryString) {
      this.bounds = this.boundsQueryString.split("%2C");
      this.map.fitBounds([
        [this.bounds[0], this.bounds[1]],
        [this.bounds[2], this.bounds[3]]
      ]);
    }

    this.addDefaultControlsToMap();
    this.setMoveEndListener();
  };

  this.addDefaultControlsToMap = function() {
    var loadingControl = L.Control.loading({
      separate: true
    })

    var sidebar = L.control.sidebar('sidebar', {
      position: 'right'
    });

    this.map.addControl(loadingControl);
    this.map.addControl(L.Control.geocoder());
    this.map.addControl(sidebar);
  };

  this.addBaseMaps = function(baseMaps) {
    this.baseLayersControl = L.control.layers(baseMaps);
    this.map.addControl(this.baseLayersControl);
  };

  this.addMarkerLayer = function(toBeAddedMarkerLayer) {
    /*
     Pass markerLayerObj in format:
     {
      name: 'points'
      layer: new L.LayerGroup()
     }
     This will get added to the this.markerLayers so that this layer can
       be accessed as +this.markerLayers.points+
    */

    markerLayer = {};
    markerLayer[toBeAddedMarkerLayer.name] = toBeAddedMarkerLayer.layer;

    if(_.has(this.markerLayers, toBeAddedMarkerLayer.name)) {
      throw("Marker Layer with name: "
              + toBeAddedMarkerLayer.name
              + " already exits");
    } else {
      _.extend(this.markerLayers, markerLayer);
      this.map.addLayer(this.markerLayers[toBeAddedMarkerLayer.name]);
    }
  };

  this.addLinkButton = function(toBeAddedLinkButton) {
    /*
     Pass linkButtonOb in format:
     {
      ref: 'newPoint'
      name: 'Click here to add new point'
      onClick: function() {  }
     }
     This will get added to the this.linkButtons so that this layer can
       be accessed as +this.linkButtons.newPoint+
    */

    linkButton = {};
    linkButton[toBeAddedLinkButton.ref] = L.control.link_button({
      text: toBeAddedLinkButton.text,
      onclick: toBeAddedLinkButton.onclick
    });

    if(_.has(this.linkButtons, toBeAddedLinkButton.ref)) {
      throw("Marker Layer with name: "
              + toBeAddedLinkButton.name
              + " already exits");
    } else {
      _.extend(this.linkButtons, linkButton);
      this.map.addControl(
       this.linkButtons[toBeAddedLinkButton.ref]
      );
    }
  };

  this.setMoveEndListener = function() {
    var _this = this;
    this.map.on('moveend', function() {
      console.log(_this);
      _this.debouncedDataLoad();
    });
  };

  this.dataLoader = function() {
    // Override this function to load the data.
    throw("PgisMap#dataLoader: This function needs to be overriden");
  };

  this.callDataLoader = function() {
    // DO NOT OVERRIDE THIS FUNCTION

    // This function gets called from _.debounce
    // We pass this function to _.debounce instead of +this.dataLoader+
    //   because _.debounce call wouldn't pick up overrides on the
    //   function that is passed to it.
    //   So, if we keep this function as an mediating function the overridden
    //   +dataLoader+ gets called.
    this.dataLoader();
  }

  this.debouncedDataLoad = _.debounce(this.callDataLoader, 1000);
};
