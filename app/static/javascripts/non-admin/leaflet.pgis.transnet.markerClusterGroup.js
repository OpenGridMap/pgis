L.PgisTransnetMarkerClusterGroup = L.MarkerClusterGroup.extend({

    options: {
        transnetDataId: undefined,
        transnetLayer: undefined,
        zoomToBoundsOnClick: false,
        // Add these css classes to the Cluster marker icon when
        //  clustered. These classes won't appear when Markers are shown.
        defaultIconCssClasses: ['default'],
        highlightIconCssClasses: ['highlighted']
    },

    // Override the default icon creation function.
    _defaultIconCreateFunction: function (cluster) {
        var childCount = cluster.getChildCount();

        var c = ' marker-cluster-';

        if (childCount < 10) {
            c += 'small';
        } else if (childCount < 100) {
            c += 'medium';
        } else {
            c += 'large';
        }

        //TODO: change the relation-id class
        return new L.DivIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: "relation-id-" + this.transnetDataId + ' marker-cluster' + c,
            iconSize: new L.Point(40, 40)
        });
    },



    addHighlightStyle: function () {
        var _this = this;

        _.each(this.options.highlightIconCssClasses, function (cssClass) {
            $(_this._relationClassSelector()).addClass(cssClass)
        })

        // Change to highlight icon on the markers in this cluster.
        // This assumes all the child layers in this clusterGroup are
        // markers - L.Marker
        this.eachLayer(function (layer) {
            layer.setIcon(_this.getMarkerHighlightIcon());
        });
    },

    removeHighlightStyle: function () {
        var _this = this;

        // Get all highlight classes into an array and remove em all from the
        //   DOM element
        highlightClasses = this.options.highlightIconCssClasses.concat(
            this.options.highlightForExportIconCssClasses
        )
        _.each(highlightClasses, function (cssClass) {
            $(_this._relationClassSelector()).removeClass(cssClass)
        })

        // This assumes all the child layers in this clusterGroup are
        // markers - L.Marker
        this.eachLayer(function (layer) {
            layer.setIcon(_this.getMarkerDefaultIcon());
        });
    },

    getMarkerHighlightForExportIcon: function () {
        return new L.Icon({
            iconUrl: '/static/images/marker-icon-dark-green.png',
            shadowUrl: '/static/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
    },

    getMarkerDefaultIcon: function () {
        return new L.Icon({
            iconUrl: '/static/images/marker-icon-red.png',
            shadowUrl: '/static/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
    },

    getMarkerHighlightIcon: function () {
        return new L.Icon({
            iconUrl: '/static/images/marker-icon.png',
            shadowUrl: '/static/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
    },

    _bindEvents: function () {
        var _this = this;

        this.on("clustermouseover", function (e) {
            _this.options.transnetLayer.fire('mouseover', e);
        });

        this.on("clustermouseout", function (e) {
            _this.options.transnetLayer.fire('mouseout', e);
        });

        // send the click event to transnet
        this.on("clusterclick", function (e) {
            _this.options.transnetLayer.fire("click", e);
        });

        L.MarkerClusterGroup.prototype._bindEvents.call(this);
    },

    //TODO: change the relation-id class
    _relationClass: function () {
        return "relation-id-" + this.options.relationId;
    },

    //TODO: change the relation-id class
    _relationClassSelector: function () {
        return "." + this._relationClass();
    }
});

L.PgisTransnetMarkerClusterGroup = function (options) {
    return new L.PgisTransnetMarkerClusterGroup(options);
};