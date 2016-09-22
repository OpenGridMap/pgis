L.PgisTransnetFeatureGroup = L.FeatureGroup.extend({
    isHighlightedForSidebar: false,

    initialize: function (transnetData, layers) {
        L.FeatureGroup.prototype.initialize.call(this, layers);

        this.transnetData = transnetData;
        this._initMarkerClusterGroup();
        this._handleTransnetPoints();
        this._handleTransnetPowerlines();
        this._bindCustomEvents();
    },


    highlightForSidebar: function () {
        this.isHighlightedForSidebar = true;
        this._markersClusterGroup.addHighlightStyle();
        this.setStyle({color: "blue"});
    },

    removeHighlightForSidebar: function () {
        this.isHighlightedForSidebar = false;
        this._markersClusterGroup.removeHighlightStyle();
        this.setStyle({color: "red"});

    },

    _initMarkerClusterGroup: function () {
        this._markersClusterGroup = L.PgisTransnetMarkerClusterGroup({
            transnetDataId: this.transnetData.id,
            transnetLayer: this
        })
    },

    _handleTransnetPowerlines: function () {
        var _this = this;

        _.each(this.transnetData.powerlines, function (line) {
            var polyline = L.polyline(line.latlngs);
            polyline.data = polyline.properties;
            polyline.setStyle({color: 'red'});

            _this.addLayer(polyline);
        });
    },

    _handleTransnetPoints: function () {
        var _this = this;
        var markers = [];

        // Create markers for each point and push them to MarkerClusterGroup
        _.each(this.transnetData.points, function (point) {
            var marker = new L.Marker(point.latlng);
            marker.data = point.properties;
            marker.setIcon(_this._markersClusterGroup.getMarkerDefaultIcon())
            markers.push(marker);
        });

        this._markersClusterGroup.addLayers(markers);
        this.addLayer(this._markersClusterGroup);
    },

    _bindCustomEvents: function () {
        var _this = this;

        this.on("mouseover", function (e) {
            // Change colors only if not highlighted for sidebar
            if (!_this.isHighlightedForSidebar) {
                _this._markersClusterGroup.addHighlightStyle();
                e.target.setStyle({color: "blue"});
            }
        });

        this.on("mouseout", function (e) {
            // Change colors only if not highlighted for sidebar
            if (!_this.isHighlightedForSidebar) {
                _this._markersClusterGroup.removeHighlightStyle();
                e.target.setStyle({color: "red"});
            }
        });
    }
})

L.PgisTransnetFeatureGroup = function (transnetData, layers) {
    return new L.PgisTransnetFeatureGroup(transnetData, layers);
}