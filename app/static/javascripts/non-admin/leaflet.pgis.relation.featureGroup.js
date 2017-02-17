// Extend the behaviour of leaflet's L.FeatureGroup and customise for the
// PGIS project.
//
// Author: Sri Vishnu Totakura <t.srivishnu@gmail.com>

L.PgisRelationFeatureGroup = L.FeatureGroup.extend({
    isHighlightedForSidebar: false,
    isHighlightedForExport: false,
    colorHash: new ColorHash({saturation: 1}),


    initialize: function (relation, layers) {
        L.FeatureGroup.prototype.initialize.call(this, layers);

        this.relation = relation;
        this.visibleVoltages = [];
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

    voltageColor: function (voltage) {
        var _this = this;
        var color = '#ff0000';
        var chosenVoltage = -1;
        var colors = ['#FF0000', '#00FFFF', '#0000FF', '#0000A0', '#ADD8E6', '#800080', '#FFFF00', '#00FF00', '#FF00FF'
            , '#FFA500', '#A52A2A', '#800000', '#008000', '#808000', '#254117', '#7D0552'];
        try {
            if (voltage) {
                if (voltage.constructor === Array) {
                    if (voltage.length == 1) {
                        chosenVoltage = parseInt(voltage[0])
                    }
                    else {
                        chosenVoltage = Math.max.apply(null, voltage)
                    }
                }
                else {
                    chosenVoltage = parseInt(voltage)
                }
            }
            var index = _this.visibleVoltages.indexOf(chosenVoltage);
            if (index <= -1) {
                _this.visibleVoltages.push(voltage);
            }
            if (chosenVoltage >= 0) {
                //color = this.colorHash.hex(chosenVoltage.toString());
                var colorPick = Math.floor(chosenVoltage / 50000);
                if (colorPick <= 15)
                    return colors[colorPick];
            }
        }
        catch (err) {
            console.error(err);
        }
        return color;
    },

    removeHighlightForExport: function () {
        this.isHighlightedForExport = false;
        this._markersClusterGroup.removeHighlightStyle();
        this.setStyle({
            color: this.voltageColor(this.relation.properties.tags.voltage)
        });
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
            this.setStyle({
                color: this.voltageColor(this.relation.properties.tags.voltage)
            });
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
            polyline.data = line.properties;
            polyline.setStyle({
                color: _this.voltageColor(_this.relation.properties.tags.voltage)
            });

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
            marker.setIcon(_this._markersClusterGroup.getMarkerDefaultIcon());
            markers.push(marker);

            if (point.latlngs !== 'undefined') {
                var polyline = L.polyline(point.latlngs);
                polyline.data = point.properties;
                polyline.setStyle({
                    color: _this.voltageColor(_this.relation.properties.tags.voltage)
                });

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
                e.target.setStyle({
                    color: _this.voltageColor(e.target.relation.properties.tags.voltage)
                });
            }
        });
    }
})

L.pgisRelationFeatureGroup = function (relation, layers) {
    return new L.PgisRelationFeatureGroup(relation, layers);
}
