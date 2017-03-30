function PgisMap() {

    this.lat = MiscHelpers.getQueryString("lat");
    this.lng = MiscHelpers.getQueryString("long");
    this.boundsQueryString = MiscHelpers.getQueryString("bounds");
    this.zoom = MiscHelpers.getQueryString("zoom") || 15;
    this.point_id = MiscHelpers.getQueryString("point_id");
    this.bounds = undefined;
    this.center = undefined;
    this.map = undefined; // Leaflet's map object
    this.layerControl = undefined;
    this.baseLayer = undefined;
    this.sidebar = undefined;
    this.transnetFilterSidebar = undefined;
    this.transnetOperationsSidebar = undefined;
    this.transnetValidationsSidebar = undefined;
    this.contributionFilterSidebar = undefined;
    this.selectedPoint = null; // point, currently opened in sidebar
    this.clusteredMarkers = 0;
    this.markerMap = {};
    this.linkButtons = {};
    // Add any kind of marker layers to this.markerLayers
    //   e.g: L.MarkerClusterGroup(), L.LayerGroup() etc.
    this.markerLayers = {};
    this.overlayLayers = {};

    this.selectedOverlayLayers = []; // Dynamically changed. Don't set it yourself.
    this.selectedCountries = [];
    this.selectedVoltages = [];

    this.visibleVoltages = [];

    this.selectedFilterGenral = ['voltage', 'cable', 'connection'];
    this.selectedFilterLineType = ['minor_line', 'cable', 'line'];
    this.selectedFilterStationType = ['substation', 'station', 'plant', 'generator'];

    this.voltagesLegend = undefined;

    this.createMap = function (baseLayer) {
        L.Icon.Default.imagePath = APP_IMAGES_URL;
        this.baseLayer = baseLayer;

        if (this.lat && this.lng) {
            this.center = [this.lat, this.lng];
        } else {
            this.center = [48.1333, 11.5667];
        }

        this.map = L.map('map', {
            layers: [this.baseLayer]
        }).setView(this.center, this.zoom);

        if (!this.lat && !this.lng) {
            this.map.locate({setView: true});
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
        this.bindOverlayLayerAddRemoveEvent();
        this.bindRelationClickEvent();
    };

    this.addDefaultControlsToMap = function () {
        var _this = this;
        var loadingControl = L.Control.loading({
            separate: true
        });

        this.sidebar = L.control.sidebar('sidebar', {
            position: 'right'
        });
        this.sidebar.on('hide', function () {
            if (_this.markerMap[pgisMap.selectedPoint] != null) {
                pgisMap.markerMap[pgisMap.selectedPoint].setIcon(new L.Icon.Default());
                pgisMap.selectedPoint = null;
            }

            if (typeof(_this.selectedOverlayLayers[0]) != 'undefined' &&
                typeof(_this.overlayLayers[_this.selectedOverlayLayers[0]].lastClickedRelationFeatureLayer) != 'undefined') {
                _this.overlayLayers[_this.selectedOverlayLayers[0]].lastClickedRelationFeatureLayer.removeHighlightForSidebar();
                _this.overlayLayers[_this.selectedOverlayLayers[0]].lastClickedRelationFeatureLayer = undefined
            }
        });

        this.transnetFilterSidebar = L.control.sidebar('transnet-filter-sidebar', {
            position: 'left'
        });

        this.contributionFilterSidebar = L.control.sidebar('contribution-filter-sidebar', {
            position: 'left'
        });

        this.transnetOperationsSidebar = L.control.sidebar('transnet-operations-sidebar', {
            position: 'right'
        });

        this.transnetValidationsSidebar = L.control.sidebar('transnet-validations-sidebar', {
            position: 'left'
        });

        this.map.addControl(loadingControl);
        this.map.addControl(L.Control.geocoder());
        this.map.addControl(this.sidebar);
        this.map.addControl(this.transnetFilterSidebar);
        this.map.addControl(this.contributionFilterSidebar);
        this.map.addControl(this.transnetOperationsSidebar);
        this.map.addControl(this.transnetValidationsSidebar);

    };

    this.addBaseMaps = function (baseMaps) {
        this.layerControl = L.control.layers(baseMaps);
        this.map.addControl(this.layerControl);
    };

    this.addOverlayLayer = function (toBeAddedOverlayLayer) {
        // Pass layer in format:
        // {
        //    name: 'Relations',
        //    layer: new L.LayerGroup()
        //    ref: 'relations'
        // }
        //
        // This gets added to +this.overlayLayers so that it can be
        //  access with the +ref+ attribute. E.g., this.overlayLayers.relations

        overlayLayer = {};
        overlayLayer[toBeAddedOverlayLayer.ref] = {
            name: toBeAddedOverlayLayer.name,
            layer: toBeAddedOverlayLayer.layer
        };

        if (_.has(this.overlayLayers, toBeAddedOverlayLayer.ref)) {
            throw("Overlay Layer with ref: "
            + toBeAddedOverlayLayer.ref
            + " already exits");
        } else {
            _.extend(this.overlayLayers, overlayLayer);

            this.layerControl.addOverlay(
                toBeAddedOverlayLayer.layer,
                toBeAddedOverlayLayer.name
            )
        }
    };

    this.addMarkerLayer = function (toBeAddedMarkerLayer) {
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

        if (_.has(this.markerLayers, toBeAddedMarkerLayer.name)) {
            throw("Marker Layer with name: "
            + toBeAddedMarkerLayer.name
            + " already exits");
        } else {
            _.extend(this.markerLayers, markerLayer);
            this.map.addLayer(this.markerLayers[toBeAddedMarkerLayer.name]);
        }
    };

    this.addLinkButton = function (toBeAddedLinkButton) {
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
            onclick: toBeAddedLinkButton.onclick,
            ref: toBeAddedLinkButton.ref,
            isVisible: true // because its right away added to the map.
        });

        if (_.has(this.linkButtons, toBeAddedLinkButton.ref)) {
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

    this.hideLinkButton = function (linkButton) {
        linkButton.removeFrom(this.map);
        linkButton.options.isVisible = false;
    };

    this.showLinkButton = function (linkButton) {
        if (linkButton.options.isVisible) {
            console.log("Button already on map: " + linkButton.options.ref);
        } else {
            linkButton.addTo(this.map);
            linkButton.options.isVisible = true;
        }
    };

    this.setMoveEndListener = function () {
        var _this = this;
        this.map.on('moveend', function () {
            _this.debouncedDataLoad();
        });
    };

    this.baseMapDataLoader = function () {
        // Override this function to load the data on the base default map.
        throw("PgisMap#baseMapDataLoader: This function needs to be overriden");
    };

    this.callDataLoader = function () {
        // DO NOT OVERRIDE THIS FUNCTION

        // This function gets called from _.debounce
        // We pass this function to _.debounce instead of +this.baseMapDataLoader+
        //   because _.debounce call wouldn't pick up overrides on the
        //   function that is passed to it.
        //   So, if we keep this function as a mediating function, the overridden
        //   +baseMapDataLoader+ gets called.
        this.baseMapDataLoader();
    };

    this.onOverlayAdd = function (layer) {
    };// override these as needed
    this.onOverlayRemove = function (layer) {
    }; //override these as needed.

    this.bindOverlayLayerAddRemoveEvent = function () {
        var _this = this;

        this.map.addEventListener("overlayadd", function (layer) {
            _this.selectedOverlayLayers.push(layer.name.toLowerCase());
            _this.onOverlayAdd(layer);
        });

        this.map.addEventListener("overlayremove", function (layer) {
            // First remove the overrlay layer from _this.selectedOverlayLayers
            var selectedLayerIndex = _this.selectedOverlayLayers.indexOf(layer.name.toLowerCase());
            if (selectedLayerIndex > -1) {
                _this.selectedOverlayLayers.splice(selectedLayerIndex, 1);
            }

            _this.onOverlayRemove(layer);
        });
    };

    this.bindRelationClickEvent = function () {
        var _this = this;
        this.map.addEventListener("relation-click", function (data) {
            relationFeatureLayer = data.relationFeatureLayer;

            _this.overlayLayers[_this.selectedOverlayLayers[0]]
                .lastClickedRelationFeatureLayer = relationFeatureLayer;

            relationFeatureLayer.highlightForSidebar();
            MapHelpers.setSidebarContentToLastClickedRelation(
                pgisMap,
                (JSON.parse(localStorage.getItem('selectedRelations')) || [])
            );

            if (!_this.sidebar.isVisible()) {
                _this.sidebar.show();
            }
        });
    };

    this.debouncedDataLoad = _.debounce(this.callDataLoader, 1000);
};
