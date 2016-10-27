function PgisSubmissionGalleryMap() {
    this.lat               = MiscHelpers.getQueryString("lat");
    this.lng               = MiscHelpers.getQueryString("long");
    this.boundsQueryString = MiscHelpers.getQueryString("bounds");
    this.zoom              = MiscHelpers.getQueryString("zoom") || 2;
    this.point_id          = MiscHelpers.getQueryString("point_id");
    this.bounds            = undefined;
    this.center            = undefined;
    this.map               = undefined; // Leaflet's map object
    this.layerControl      = undefined;
    this.baseLayer         = undefined;
    this.sidebar           = undefined;
    this.selectedPoint     = null; // point, currently opened in sidebar
    this.markerMap         = {};
    this.linkButtons       = {};
    // Add any kind of marker layers to this.markerLayers
    //   e.g: L.MarkerClusterGroup(), L.LayerGroup() etc.
    this.markerLayers      = {};
    this.overlayLayers     = {};
    this.galleryContainer  = $("#sidebar-content");
    this.data              = {};

    this.selectedOverlayLayers = []; // Dynamically changed. Don't set it yourself.

    this.createMap = function(baseLayer) {
        L.Icon.Default.imagePath = APP_IMAGES_URL;
        this.baseLayer = baseLayer;

        if(this.lat && this.lng) {
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
    };

    this.addDefaultControlsToMap = function() {
        var _this = this;
        var loadingControl = L.Control.loading({
            separate: true
        });

        this.map.addControl(loadingControl);
        this.map.addControl(L.Control.geocoder());
        this.map.addControl(this.sidebar);
    };

    this.addBaseMaps = function(baseMaps) {
        this.layerControl = L.control.layers(baseMaps);
        this.map.addControl(this.layerControl);
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
}
