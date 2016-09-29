// Extend the behaviour of leaflet's L.FeatureGroup and customise for the
// PGIS project.
//
// Author: Sri Vishnu Totakura <t.srivishnu@gmail.com>

L.PgisRelationFeatureGroup = L.FeatureGroup.extend({
    isHighlightedForSidebar: false,
    isHighlightedForExport: false,

    initialize: function (relation, layers) {
        L.FeatureGroup.prototype.initialize.call(this, layers);

        this.relation = relation;
        this._initMarkerClusterGroup();
        this._handleRelationPoints();
        this._handleRelationPowerlines();
        this._bindCustomEvents();
    },

    highlightForExport: function () {
        this.isHighlightedForExport = true;
        this._markersClusterGroup.addHighlightStyleForExport();
        this.setStyle({color: 'black'});
    },

    removeHighlightForExport: function () {
        this.isHighlightedForExport = false;
        this._markersClusterGroup.removeHighlightStyle();
        this.setStyle({color: 'red'});
    },

    highlightForSidebar: function () {
        this.isHighlightedForSidebar = true;
        this._markersClusterGroup.addHighlightStyle();
        this.setStyle({color: "blue"});
    },

    removeHighlightForSidebar: function () {
        this.isHighlightedForSidebar = false;

        if (this.isHighlightedForExport) {
            this.highlightForExport();
        } else {
            this._markersClusterGroup.removeHighlightStyle();
            this.setStyle({color: "red"});
        }
    },

    _initMarkerClusterGroup: function () {
        this._markersClusterGroup = L.pgisRelationMarkerClusterGroup({
            relationId: this.relation.id,
            relationLayer: this
        })
    },

    _handleRelationPowerlines: function () {
        var _this = this;

        _.each(this.relation.powerlines, function (line) {
            var polyline = L.polyline(line.latlngs);
            polyline.data = polyline.properties;
            polyline.setStyle({color: 'red'});

            _this.addLayer(polyline);
        });
    },

    _handleRelationPoints: function () {
        var _this = this;
        var markers = [];

        // Create markers for each point and push them to MarkerClusterGroup
        _.each(this.relation.points, function (point) {
            var marker = new L.Marker(point.latlng);
            marker.data = point.properties;
            marker.setIcon(_this._markersClusterGroup.getMarkerDefaultIcon())
            markers.push(marker);

            if (point.latlngs !== 'undefined') {
                var polyline = L.polyline(point.latlngs);
                polyline.data = polyline.properties;
                polyline.setStyle({color: 'red'});

                _this.addLayer(polyline);
            }


        });

        this._markersClusterGroup.addLayers(markers);
        this.addLayer(this._markersClusterGroup);
    },

    _bindCustomEvents: function () {
        var _this = this;

        this.on("mouseover", function (e) {
            // Change colors only if not highlighted for sidebar or export
            if (!_this.isHighlightedForSidebar && !_this.isHighlightedForExport) {
                _this._markersClusterGroup.addHighlightStyle();
                e.target.setStyle({color: "blue"});
            }
        });

        this.on("mouseout", function (e) {
            // Change colors only if not highlighted for sidebar or export
            if (!_this.isHighlightedForSidebar && !_this.isHighlightedForExport) {
                _this._markersClusterGroup.removeHighlightStyle();
                e.target.setStyle({color: "red"});
            }
        });
    }
})

L.pgisRelationFeatureGroup = function (relation, layers) {
    return new L.PgisRelationFeatureGroup(relation, layers);
}
